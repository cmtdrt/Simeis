#!/usr/bin/env python3
import os
import sys
import uuid
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sdk.python import SimeisSDK # noqa: E402

DEFAULT_HOST = os.environ.get("SIMEIS_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("SIMEIS_PORT", "8080"))


def unique_username():
    return f"test_{uuid.uuid4().hex[:8]}"


class SimeisFunctionalTest(unittest.TestCase):
    """Liste des tests fonctionnels

    Exemple de scénario :
    - On créé un nouveau joueur
    - Son argent de départ est X
    - On achète un vaisseau
    - La transaction doit réussir
    - Notre argent doit avoir diminué
    - On achète un module de Miner
    - La transaction doit réussir
    - Notre argent doit avoir encore diminué
    """

    @classmethod
    def setUpClass(cls):
        cls.username = unique_username()
        cls.sdk = SimeisSDK(cls.username, DEFAULT_HOST, DEFAULT_PORT)

    def test_01_new_player_has_money(self):
        status = self.sdk.get_player_status()

        self.assertGreater(
            status.get("money", 0), 0.0, "Le joueur doit commencer avec de l'argent"
        )
        self.assertEqual(
            len(status.get("ships", [])),
            0,
            "Un nouveau joueur ne doit pas avoir de vaisseau",
        )
        self.assertGreater(
            len(status.get("stations", [])),
            0,
            "Le joueur doit disposer d'au moins une station",
        )

        cls = self.__class__
        cls.station_id = status["stations"][0]
        cls.starting_money = status["money"]

    def test_02_buy_ship(self):
        status_before = self.sdk.get_player_status()
        station_id = getattr(self.__class__, "station_id")
        self.assertEqual(
            len(status_before["ships"]),
            0,
            "Le joueur doit encore être sans vaisseau avant l'achat",
        )

        ships = self.sdk.shop_list_ship(station_id)
        self.assertGreater(
            len(ships), 0, "La boutique doit proposer au moins un vaisseau"
        )

        cheapest = ships[0]
        self.assertLessEqual(
            cheapest["price"],
            status_before["money"],
            "Le joueur doit pouvoir acheter le vaisseau le moins cher",
        )

        buy_ship_resp = self.sdk.buy_ship(station_id, cheapest["id"])
        self.assertIn(
            "id", buy_ship_resp, "L'achat du vaisseau doit renvoyer un identifiant"
        )
        self.assertEqual(
            buy_ship_resp["id"],
            cheapest["id"],
            "L'identifiant du vaisseau acheté doit correspondre a celui choisi",
        )

        status_after = self.sdk.get_player_status()
        self.assertEqual(
            len(status_after["ships"]),
            1,
            "Après l'achat, le joueur doit posséder un vaisseau",
        )
        self.assertLess(
            status_after["money"],
            status_before["money"],
            "L'argent du joueur doit diminuer après l'achat du vaisseau",
        )

        cls = self.__class__
        cls.ship_id = buy_ship_resp["id"]
        cls.money_after_ship = status_after["money"]
        cls.station_id = station_id

    def test_03_buy_miner_module(self):
        cls = self.__class__
        if not hasattr(cls, "ship_id"):
            self.skipTest(
                "Le vaisseau n'a pas été acheté, impossible de tester le module"
            )

        modules = self.sdk.shop_list_modules(self.station_id)
        self.assertIn("Miner", modules, "Le magasin doit proposer un module mineur")

        module_cost = modules["Miner"]
        buy_module_resp = self.sdk.buy_module_on_ship(
            self.station_id, self.ship_id, "Miner"
        )

        self.assertIn(
            "id", buy_module_resp, "L'achat du module doit renvoyer un identifiant"
        )
        self.assertIn(
            "cost", buy_module_resp, "L'achat du module doit renvoyer un coût"
        )
        cls.module_id = buy_module_resp["id"]
        self.assertEqual(
            buy_module_resp["cost"],
            module_cost,
            "Le prix du module doit correspondre au prix attendu",
        )

        status_after_module = self.sdk.get_player_status()
        self.assertLess(
            status_after_module["money"],
            self.money_after_ship,
            "L'argent du joueur doit diminuer après l'achat du module",
        )

        cls = self.__class__
        ship_status = self.sdk.get_ship_status(cls.ship_id)
        self.assertIn(
            "modules", ship_status, "Le vaisseau doit contenir un champ modules"
        )
        self.assertTrue(
            any(
                module.get("modtype") == "Miner"
                for module in ship_status["modules"].values()
            ),
            "Le vaisseau doit être équipé d'un modules mineur",
        )

    def test_04_hire_operator_and_assign_to_module(self):
        cls = self.__class__
        if not hasattr(cls, "ship_id"):
            self.skipTest(
                "Le vaisseau n'a pas été acheté, impossible de tester le recrutement"
            )

        hire_resp = self.sdk.hire_crew(self.station_id, "operator")
        self.assertIn(
            "id", hire_resp, "L'embauche doit renvoyer un identifiant de crew"
        )

        assign_resp = self.sdk.assign_crew_to_ship(
            self.station_id, cls.ship_id, hire_resp["id"], cls.module_id
        )
        self.assertIsNotNone(
            assign_resp, "L'assignation du crew au module doit réussir"
        )

        ship_status = self.sdk.get_ship_status(cls.ship_id)
        self.assertIn(
            "modules", ship_status, "Le vaisseau doit contenir un champ modules"
        )
        self.assertTrue(
            any(
                module.get("operator") == hire_resp["id"]
                for module in ship_status["modules"].values()
            ),
            "Le crew doit être affecté au module Miner",
        )

    def test_05_summary(self):
        cls = self.__class__
        status = self.sdk.get_player_status()
        print("\n--- Résumé ---")
        print(f"Joueur : {self.username}")
        print(f"Stations: {cls.station_id}")
        print(f"Vaisseau: {getattr(cls, 'ship_id', 'inconnu')}")
        print(f"Argent : {status['money']}")
        print(f"Vaisseaux : {len(status['ships'])}")


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(
        unittest.defaultTestLoader.loadTestsFromTestCase(SimeisFunctionalTest)
    )
    sys.exit(0 if result.wasSuccessful() else 1)
