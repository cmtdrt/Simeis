import sys
import time
import random
import math
import json
import os


REGRESSIONS_FILE = "regressions.json"


def load_regressions():
    """Charge les regressions depuis le fichier JSON"""
    if os.path.exists(REGRESSIONS_FILE):
        with open(REGRESSIONS_FILE, "r") as f:
            return json.load(f)
    return {"addition": [], "distance": []}


def save_regressions(regressions):
    """Sauvegarde les regressions dans le fichier JSON"""
    with open(REGRESSIONS_FILE, "w") as f:
        json.dump(regressions, f, indent=2)


# Charge les regressions connues
known_regressions = load_regressions()


def create_property_based_test(test_name, f, regressions=[], time_test=10):
    tstart = time.time()
    i = 0
    found_errors = list(regressions)  # Copie les regressions connues
    while (time.time() - tstart) < time_test:
        if i < len(regressions):
            seed = regressions[i]
        else:
            seed = random.randrange(0, 2**64)
        random.seed(seed)
        try:
            f(seed)
            print("Test", f.__name__, i, "OK")
        except AssertionError as err:
            print("Test", f.__name__, "failed with seed", seed)
            print(err)
            if seed not in found_errors:
                found_errors.append(seed)
        i += 1

    # Met à jour et sauvegarde les regressions
    if found_errors != regressions:
        known_regressions[test_name] = found_errors
        save_regressions(known_regressions)
        print(f"✓ Regressions sauvegardées pour {test_name}: {found_errors}")

    return found_errors


### Example


def get_dist(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))


def addition(seed):
    _x = random.randrange(0, 10000)
    _y = random.randrange(0, 10000)
    _z = random.randrange(0, 10000)

    # Exercice:    Tester les additions
    expected_xy = _x + _y
    assert expected_xy == _y + _x, (
        f"[seed={seed}] Addition non commutative: {_x} + {_y} != {_y} + {_x}"
    )
    assert (_x + _y) + _z == _x + (_y + _z), (
        f"[seed={seed}] Addition non associative: ({_x} + {_y}) + {_z} != {_x} + ({_y} + {_z})"
    )
    assert _x + 0 == _x, f"[seed={seed}] Addition avec zéro échoue: {_x} + 0 != {_x}"


def distance(seed):
    x1 = random.randrange(-100, 100)
    y1 = random.randrange(-100, 100)
    z1 = random.randrange(-100, 100)
    _a = (x1, y1, z1)

    x2 = random.randrange(-100, 100)
    y2 = random.randrange(-100, 100)
    z2 = random.randrange(-100, 100)
    _b = (x2, y2, z2)

    # Exercice:     Tester la distance entre le point A et le point B
    dist_ab = get_dist(_a, _b)
    dist_ba = get_dist(_b, _a)
    assert dist_ab >= 0, f"[seed={seed}] Distance négative calculée: {dist_ab}"
    assert dist_ab == dist_ba, (
        f"[seed={seed}] Distance non symétrique: dist({_a}, {_b}) != dist({_b}, {_a})"
    )

    dx = x1 - x2
    dy = y1 - y2
    dz = z1 - z2
    expected = math.sqrt(dx * dx + dy * dy + dz * dz)
    assert math.isclose(dist_ab, expected, rel_tol=1e-12), (
        f"[seed={seed}] Distance incorrecte: {dist_ab} != {expected} pour {_a} et {_b}"
    )


if __name__ == "__main__":
    time_addition = 3
    time_distance = 10

    if len(sys.argv) > 1:
        if sys.argv[1] == "heavy":
            time_addition = 140  # ~2m20s
            time_distance = 140  # ~2m20s
        else:
            try:
                time_addition = int(sys.argv[1])
                time_distance = int(sys.argv[1])
            except ValueError:
                print(f"Usage: python propertybased.py [heavy|<seconds>]")
                sys.exit(1)

    regressions_addition = create_property_based_test(
        "addition",
        addition,
        regressions=known_regressions["addition"],
        time_test=time_addition,
    )
    regressions_distance = create_property_based_test(
        "distance",
        distance,
        regressions=known_regressions["distance"] + [4480881574280375424],
        time_test=time_distance,
    )
