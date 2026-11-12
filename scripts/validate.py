#!/usr/bin/env python3
"""Validate examples against the DHR and DLS schemas and run negative tests.
Usage: python scripts/validate.py   (run from the repository root)"""
import copy, json, sys, pathlib
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent

class Loader(yaml.SafeLoader):
    pass
# keep dates as strings so JSON Schema "format: date" sees text
Loader.yaml_implicit_resolvers = {
    k: [r for r in v if r[0] != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
load_yaml = lambda p: yaml.load(open(p), Loader=Loader)
load_json = lambda p: json.load(open(p))
V = lambda s: Draft202012Validator(s, format_checker=FormatChecker())

dhr_s = load_json(ROOT / "schemas/dhr-0.1.json")
dls_s = load_json(ROOT / "schemas/dls-0.1.json")
for s in (dhr_s, dls_s):
    Draft202012Validator.check_schema(s)

fail = 0
dhr = load_yaml(ROOT / "examples/dhr-asi04-0001.yaml")
dls = load_yaml(ROOT / "examples/dls-asi02-0005.yaml")
for name, s, d in (("dhr-asi04-0001", dhr_s, dhr), ("dls-asi02-0005", dls_s, dls)):
    errs = list(V(s).iter_errors(d))
    print(name, "OK" if not errs else "FAIL")
    for e in errs:
        print("  ", list(e.path), e.message[:140])
        fail += 1

def must_reject(label, schema, doc, mutate):
    d = copy.deepcopy(doc)
    mutate(d)
    rejected = bool(list(V(schema).iter_errors(d)))
    print(("rejected: " if rejected else "NOT REJECTED: ") + label)
    return rejected

tests = [
    ("DHR unknown OWASP id", dhr_s, dhr, lambda d: d["threat"].update(owasp_asi="ASI11")),
    ("DHR t-invest without response", dhr_s, dhr, lambda d: d.pop("response")),
    ("DHR live without reviewer", dhr_s, dhr, lambda d: (d.update(status="live"), d["provenance"].pop("reviewed_by"))),
    ("DHR validated without tests", dhr_s, dhr, lambda d: (d.update(status="validated"), d.pop("tests"))),
    ("DHR unknown top-level field", dhr_s, dhr, lambda d: d.update(foo=1)),
    ("DHR bad readiness", dhr_s, dhr, lambda d: d["prerequisites"].update(min_readiness="T4")),
    ("DLS sequence without window", dls_s, dls, lambda d: d["logic"].pop("window")),
    ("DLS exclusion without counter_test", dls_s, dls, lambda d: d["exclusions"][0].pop("counter_test")),
    ("DLS no missing-field behavior", dls_s, dls, lambda d: d.pop("on_missing_field")),
    ("DLS no variants", dls_s, dls, lambda d: d["tests"].pop("variants")),
    ("DLS profile baseline without lookback", dls_s, dls, lambda d: d["baseline"].update(mode="profile")),
    ("DLS version as number", dls_s, dls, lambda d: d.update(dls=0.1)),
]
for t in tests:
    if not must_reject(*t):
        fail += 1

ext = copy.deepcopy(dls)
ext["x-vendor-note"] = "ok"
ok = not list(V(dls_s).iter_errors(ext))
print("x- extension accepted:", ok)
fail += 0 if ok else 1
sys.exit(1 if fail else 0)
