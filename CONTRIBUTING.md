# Contributing

Contributions are welcome as issues and pull requests:
- new or corrected hypotheses (catalog/)
- validated fixtures (fixtures/)
- mappings to other schemas
- adapter reports, including lost semantics
- field reports from real deployments
- evidence that should change a threshold or a requirement

## Before you open a pull request
1. For a material change, open an issue first and wait for the comment period (see GOVERNANCE.md).
2. Run `pip install pyyaml jsonschema` and `python scripts/validate.py`; it must pass.
3. Keep requirement IDs stable; never reuse one.
4. Add a line to CHANGELOG.md under "Unreleased".
5. Do not include real customer data, secrets or non-public telemetry in fixtures. Redact or synthesize.

## Challenging a requirement
Use the "Challenge a requirement" issue template. Say which ID, why it is wrong, missing or unworkable, and what you would do instead.

## Licensing of contributions
By contributing you agree your text is released under CC BY 4.0 and your schemas, scripts and code under Apache-2.0. Whether a sign-off (DCO) or contributor agreement is required is an open decision.

## Conduct
See CODE_OF_CONDUCT.md.
