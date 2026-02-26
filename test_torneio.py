import unittest
from app import criar_fase, avancar_confronto, torneio

class TestTorneio(unittest.TestCase):

    def test_criacao_fase(self):
        participantes = [
            {"nome": "A"},
            {"nome": "B"},
            {"nome": "C"},
            {"nome": "D"},
        ]

        criar_fase(participantes)

        self.assertEqual(len(torneio["confrontos"]), 2)

    def test_avancar_confronto(self):
        participantes = [
            {"nome": "A"},
            {"nome": "B"},
        ]

        criar_fase(participantes)

        confronto = torneio["confrontos"][0]
        confronto["votos_esquerda"] = 5
        confronto["votaram"] = ["1","2","3","4","5"]

        avancar_confronto()

        self.assertEqual(torneio["campeao"]["nome"], "A")

if __name__ == "__main__":
    unittest.main()