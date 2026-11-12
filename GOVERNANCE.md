# Governance

Status: v0.1. Items marked (proposed) are intentions, not facts.

## Stewardship (proposed)
The author acts as sole maintainer until a maintainers group exists. Decisions are made in public issues with the rationale recorded. A maintainers group with members from at least two organizations is a condition for version 1.0.

## Decisions
- Material changes (new or changed requirements, schema changes, conformance changes) start as an issue-based proposal, stay open for public comment for at least 14 days, and are decided by the maintainers with the rationale recorded in the issue.
- Editorial fixes (typos, clarifications that do not change meaning) can go straight to a pull request.

## Versioning
Semantic versioning for the specification and for each schema.
- MAJOR: removes or renames a requirement or required field, or makes a previously conformant claim non-conformant.
- MINOR: adds optional fields, event classes or RECOMMENDED requirements.
- PATCH: fixes wording or errors without changing meaning.
Before 1.0 a MINOR release may break compatibility; CHANGELOG.md says so.

## Stable identifiers
Requirement IDs, DHR IDs and event-class names are never reused. A deprecated item stays in the catalogue, marked deprecated, for at least one MINOR release before removal.

## Extensions
Local fields use the `x-` prefix that both schemas reserve. An extension MUST NOT change the meaning of a defined field.

## Conformance claims
Claims are self-assessed in v0.1 and worded "conformant with ASSAY version X as a [telemetry emitter | detection pack | adapter | organization]". They never imply endorsement by the project.
