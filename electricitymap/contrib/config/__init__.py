import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, NewType, Tuple

ZoneKey = NewType("ZoneKey", str)
Point = NewType("Point", Tuple[float, float])
BoundingBox = NewType("BoundingBox", List[Point])

CONFIG_DIR = Path(__file__).parent.parent.parent.parent.joinpath("config").resolve()

# Read JOSN files
ZONES_CONFIG = json.load(open(CONFIG_DIR.joinpath("zones.json")))
EXCHANGES_CONFIG = json.load(open(CONFIG_DIR.joinpath("exchanges.json")))
CO2EQ_PARAMETERS = json.load(open(CONFIG_DIR.joinpath("co2eq_parameters.json")))

# Prepare zone bounding boxes
ZONE_BOUNDING_BOXES: Dict[ZoneKey, BoundingBox] = {}
for zone_id, zone_config in ZONES_CONFIG.items():
    if "bounding_box" in zone_config:
        ZONE_BOUNDING_BOXES[zone_id] = zone_config["bounding_box"]

# Add link from subzone to the full zone
ZONE_PARENT: Dict[ZoneKey, ZoneKey] = {}
for zone_id, zone_config in ZONES_CONFIG.items():
    if "subZoneNames" in zone_config:
        for sub_zone_id in zone_config["subZoneNames"]:
            ZONE_PARENT[sub_zone_id] = zone_id

# Prepare zone neighbours
ZONE_NEIGHBOURS: Dict[ZoneKey, List[ZoneKey]] = {}


# This object represents all neighbours regardless of granularity
def generate_all_neighbours(exchanges_config) -> Dict[ZoneKey, List[ZoneKey]]:
    zone_neighbours = defaultdict(set)
    for k, v in exchanges_config.items():
        zone_1, zone_2 = k.split("->")
        pairs = [(zone_1, zone_2), (zone_2, zone_1)]
        for zone_name_1, zone_name_2 in pairs:
            zone_neighbours[zone_name_1].add(zone_name_2)
    # Sort
    return {k: sorted(v) for k, v in zone_neighbours.items()}


ALL_NEIGHBOURS: Dict[ZoneKey, List[ZoneKey]] = generate_all_neighbours(EXCHANGES_CONFIG)


for k, v in EXCHANGES_CONFIG.items():
    zone_names = k.split("->")
    pairs = [(zone_names[0], zone_names[1]), (zone_names[1], zone_names[0])]
    for zone_name_1, zone_name_2 in pairs:
        if zone_name_1 not in ZONE_NEIGHBOURS:
            ZONE_NEIGHBOURS[zone_name_1] = set()
        ZONE_NEIGHBOURS[zone_name_1].add(zone_name_2)
# we want neighbors to always be in the same order
for zone, neighbors in ZONE_NEIGHBOURS.items():
    ZONE_NEIGHBOURS[zone] = sorted(neighbors)


def emission_factors(zone_key: ZoneKey):
    override = CO2EQ_PARAMETERS["emissionFactors"]["zoneOverrides"].get(zone_key, {})
    defaults = CO2EQ_PARAMETERS["emissionFactors"]["defaults"]
    merged = {**defaults, **override}
    return dict([(k, (v or {}).get("value")) for (k, v) in merged.items()])
