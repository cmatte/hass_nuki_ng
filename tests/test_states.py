"""Sensor state keys must always be in the sensor's options (HA rejects others)."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import COMPONENT, _load

states = _load("states")

LOCK_OPTIONS = states.state_options(states.LockStates, states.OpenerStates)
DOOR_OPTIONS = states.state_options(states.DoorSensorStates)
SECURITY_OPTIONS = states.state_options(states.DoorSecurityStates)


def test_every_lock_and_opener_code_is_an_option():
    for group in (states.LockStates, states.OpenerStates):
        for s in group:
            assert states.state_key(group, s.value) in LOCK_OPTIONS


def test_options_have_no_duplicates():
    for opts in (LOCK_OPTIONS, DOOR_OPTIONS, SECURITY_OPTIONS):
        assert len(opts) == len(set(opts))


def test_known_codes():
    assert states.state_key(states.LockStates, 6) == "lock_n_go"
    assert states.state_key(states.OpenerStates, 3) == "ring_to_open_active"
    assert states.state_key(states.DoorSensorStates, 2) == "door_closed"
    assert states.state_key(states.DoorSensorStates, 4) == "door_unknown"


def test_unknown_or_missing_code_gives_no_value():
    assert states.state_key(states.LockStates, None) is None
    assert states.state_key(states.LockStates, 99) is None
    assert states.state_key(states.OpenerStates, 2) is None


def test_every_option_is_translated():
    wanted = {
        "state": LOCK_OPTIONS,
        "door_state": DOOR_OPTIONS,
        "door_security_state": SECURITY_OPTIONS,
    }
    files = [COMPONENT / "strings.json", *sorted((COMPONENT / "translations").glob("*.json"))]
    for f in files:
        data = json.loads(Path(f).read_text())
        if f.name in ("es.json", "fr.json", "pt-BR.json"):
            continue  # no entity strings yet: Home Assistant falls back to English
        sensors = data["entity"]["sensor"]
        for key, opts in wanted.items():
            assert set(sensors[key]["state"]) == set(opts), (f.name, key)
