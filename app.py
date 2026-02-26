from flask import Flask, render_template, request, redirect, session, jsonify
import json
import random

app = Flask(__name__)
app.secret_key = "segredo_super_secreto"

torneio = {}

def iniciar_torneio():
    global torneio

    with open("participantes.json", "r", encoding="utf-8") as f:
        participantes = json.load(f)

    for p in participantes:
        p["imagem"] = p["nome"] + ".png"

    random.shuffle(participantes)

    limite = min(32, len(participantes))
    if limite % 2 != 0:
        limite -= 1

    selecionados = participantes[:limite]

    torneio = {
        "max_votos": 5,
        "iniciado": False,
        "campeao": None
    }

    criar_fase(selecionados)


def criar_fase(lista_participantes):
    global torneio

    confrontos = []

    for i in range(0, len(lista_participantes), 2):
        confrontos.append({
            "esquerda": lista_participantes[i],
            "direita": lista_participantes[i+1],
            "votos_esquerda": 0,
            "votos_direita": 0,
            "votaram": []
        })

    torneio["confrontos"] = confrontos
    torneio["confronto_atual"] = 0
    torneio["vencedores"] = []
    torneio["fase"] = len(lista_participantes)

    # ⚠️ NÃO mexe em iniciado aqui
    # ⚠️ NÃO mexe em campeao aqui
    # ⚠️ NÃO mexe em max_votos aqui


def avancar_confronto():
    global torneio

    confronto = torneio["confrontos"][torneio["confronto_atual"]]

    if confronto["votos_esquerda"] > confronto["votos_direita"]:
        vencedor = confronto["esquerda"]
    else:
        vencedor = confronto["direita"]

    torneio["vencedores"].append(vencedor)

    # Se ainda tem confronto nessa fase
    if torneio["confronto_atual"] + 1 < len(torneio["confrontos"]):
        torneio["confronto_atual"] += 1
        return

    # Fase terminou
    if len(torneio["vencedores"]) == 1:
        torneio["campeao"] = torneio["vencedores"][0]
        return

    # Criar nova fase
    criar_fase(torneio["vencedores"])


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["nome"] = request.form["nome"]
        return redirect("/aguardando")

    return render_template("login.html")


@app.route("/aguardando")
def aguardando():
    if "nome" not in session:
        return redirect("/")

    if torneio.get("iniciado"):
        return redirect("/votacao")

    return render_template("aguardando.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        torneio["iniciado"] = True
        return redirect("/votacao")

    return render_template("admin.html")


@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    iniciar_torneio()
    return redirect("/admin")


@app.route("/votacao")
def votacao():
    if not torneio.get("iniciado"):
        return redirect("/aguardando")

    if torneio.get("campeao"):
        return render_template("campeao.html", campeao=torneio["campeao"])

    confronto = torneio["confrontos"][torneio["confronto_atual"]]

    return render_template(
        "votacao.html",
        confronto=confronto,
        votos_atual=len(confronto["votaram"]),
        max_votos=torneio["max_votos"],
        confronto_atual=torneio["confronto_atual"],
        fase=torneio["fase"]
    )


@app.route("/votar", methods=["POST"])
def votar():
    if "nome" not in session:
        return redirect("/")

    nome = session["nome"]
    confronto = torneio["confrontos"][torneio["confronto_atual"]]

    if nome in confronto["votaram"]:
        return redirect("/votacao")

    escolha = request.form["escolha"]
    confronto["votaram"].append(nome)

    if escolha == "esquerda":
        confronto["votos_esquerda"] += 1
    else:
        confronto["votos_direita"] += 1

    if len(confronto["votaram"]) >= torneio["max_votos"]:
        avancar_confronto()

    return redirect("/votacao")


@app.route("/status")
def status():
    if torneio.get("campeao"):
        return jsonify({"campeao": torneio["campeao"]["nome"]})

    confronto = torneio["confrontos"][torneio["confronto_atual"]]

    return jsonify({
        "votos_atual": len(confronto["votaram"]),
        "max_votos": torneio["max_votos"],
        "confronto_atual": torneio["confronto_atual"],
        "fase": torneio["fase"]
    })


iniciar_torneio()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090, debug=True)