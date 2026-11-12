# ASSAY: Evidence-Based Detection Engineering for Agentic Systems

**Status: v0.1, draft for public review.** A vendor-neutral specification and methodology. Not a product, not a standard of any standards body.

An assay is a test of what a thing is worth. ASSAY is a method for deciding what to detect in agentic systems, building those detections (with or without AI help), and proving they work before anyone relies on them.

## Why this exists

Detection teams are stretched on the old problem, while agents and MCP servers add a new class of assets that most SIEM content does not cover. Agents can now draft detections, but plausible is not verified: in the AVDA study, agent-written rules matched attack techniques well but matched reference exclusion logic rarely, and the generated code was never executed. ASSAY treats that gap as the central design problem.

## What is in it

Five layers, two tracks.

| Layer | What it specifies |
| --- | --- |
| 1. Telemetry contract | The minimum events agents and MCP servers must emit, with identity lineage and readiness levels T0 to T3 |
| 2. Threat-to-detection map | OWASP agentic risks and MITRE ATLAS turned into testable hypotheses with telemetry prerequisites |
| 3. Agentic authoring | How agents may draft detection content in a staged pipeline, and what humans own |
| 4. Validation gates | G0 static, G1 replay, G2 emulation, G3 noise budget, G4 evasion review, G5 regression |
| 5. Governed deployment | Impact tiers (T-Info, T-Invest, T-Disrupt) and authoring autonomy A0 to A3 |

Tracks: **Defend AI** (detect attacks on and by agents) and **Use AI** (use agents to author, test and tune detections).

Also in the document: Detection Hypothesis Record (DHR) and Detection Logic Specification (DLS) with JSON Schemas, a requirements catalogue with stable IDs, conformance classes and the evidence bundle, a roles table, a worked example, twelve starter hypotheses, a maturity model, a threat model, and a crosswalk to NIST CSF 2.0, NIST AI RMF, ISO/IEC 27001 and 42001, the EU AI Act, OWASP, ATLAS and ATT&CK.

## Who it is for

CISOs and security leaders who need to know what "covered" means for AI agents, and detection engineers and SOC teams who build and run the detections.

## What it is not

Not a prompt-injection classifier, a guardrail or prevention framework, an incident-response playbook, a rule collection, or a reference implementation. There is no code in this repository yet.

## Read it

- Full specification: `spec/ASSAY-v0.1.md` (or the published document link)
- Schemas: `schemas/dhr-0.1.json`, `schemas/dls-0.1.json`
- Examples: `examples/`

## How it relates to other work

ASSAY builds on Sigma, MITRE ATLAS, the OWASP Top 10 for Agentic Applications, OpenTelemetry GenAI and OCSF, and sits beside projects such as ATR, OpenTIDE, Vega Detection Skills, the Nebulock Agentic Detection Engineering Framework and the infosecb AI maturity matrix. It does not claim to be first; its claim is a combined specification covering agent telemetry, threat mapping, vendor-neutral logic, evidence gates and governed autonomy. See the "Where ASSAY fits" section.

## Conformance

Claims are self-assessed in v0.1 and are worded "conformant with ASSAY version X as a [telemetry emitter | detection pack | adapter | organization]". They never imply endorsement.

## Contributing

Issues and pull requests are welcome: corrected or new hypotheses, validated fixtures, mappings to other schemas, adapter reports, and field reports from real deployments. Material changes start as an issue and stay open for comment for at least 14 days. See `CONTRIBUTING.md`, `GOVERNANCE.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md`.

To report a flaw in the schemas or guidance that could create a detection blind spot, follow `SECURITY.md`; do not open a public issue.

## Versioning

Semantic versioning. Before 1.0, a minor release may break compatibility and the changelog says so. Requirement, DHR and event-class identifiers are never reused.

## License

Specification text: CC BY 4.0. Schemas, templates and code examples: Apache-2.0. (Proposed; maintainer to confirm before first release.)

## Name

ASSAY is a common English word; cite it as "ASSAY detection engineering". No trademark clearance has been performed.

## Repository layout

```
spec/        the specification (ASSAY-v0.1.md)
schemas/     DHR and DLS JSON Schemas
examples/    example DHR and DLS records (validated in CI)
catalog/     hypothesis records (to be added)
fixtures/    labeled test events (to be added)
templates/   pipeline starters (to be added)
scripts/     validate.py, run by CI
```

Check the schemas and examples locally: `pip install pyyaml jsonschema && python scripts/validate.py`
