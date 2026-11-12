# ASSAY: Evidence-Based Detection Engineering for Agentic Systems (v0.1 Spec and Methodology)

Version 0.1 · draft for public review

## Executive summary

ASSAY is a vendor-neutral method for building detections in the AI era: what to log, what to detect, how agents may help write detections, how to prove the detections work, and how much autonomy to grant those agents. It is a specification and methodology, not a product, and it runs on top of the SIEM, data lake or streaming stack you already have.

**The problem has three parts.**

- **Detection engineering is not keeping up.** In SANS's 2026 survey, 80% of teams say they are barely keeping pace or falling behind, and only 42% have reached CI/CD for their rules.
- **AI agents are a new attack surface that existing rules do not see.** Agents act under borrowed identities, call tools over MCP, and read untrusted content as instructions. Real incidents already exist: a malicious postmark-mcp package silently copied every email to an attacker, and a state-sponsored group used an AI coding agent for an estimated 80-90% of an intrusion campaign.
- **Attackers are also using AI inside their tooling.** Google's threat intelligence group has documented malware that queries an LLM at runtime to generate commands or rewrite itself.

**The framework in five layers.**

1. **Telemetry contract:** the minimum events from agents, MCP servers and LLM gateways that make detection possible, with identity lineage.
2. **Threat-to-detection map:** OWASP agentic risks and MITRE ATLAS techniques turned into testable detection hypotheses, each with its telemetry prerequisites.
3. **Agentic authoring:** a staged pipeline where agents draft hypotheses, rules and test data; they propose and never deploy.
4. **Validation gates:** every rule is executed against labeled logs and emulated behavior before it is eligible for production.
5. **Governed deployment:** autonomy tiers tied to the impact of the detection, with provenance, approval and rollback.

**What you get.** A portable Detection Hypothesis Record and Detection Logic Specification, a five-level maturity model, a metric set for board-level reporting, a 90-day adoption plan, and a starter catalog of agent-focused detection hypotheses.

**What it asks of you.** Three decisions: who owns detections for AI systems (security or platform engineering), which telemetry you will require from every agent deployment, and the highest autonomy tier you are willing to grant an authoring agent.

## Why now

Two trends collide in 2026: detection teams are stretched thin on the old problem, while agents and MCP servers create a new class of assets that most SIEM content does not cover. The evidence below is what ASSAY is built on.

| Evidence | What it shows |
| --- | --- |
| [SANS and Anvilogic, State of Detection Engineering 2026](https://www.anvilogic.com/report/state-of-detection-engineering) | 62% version-control rules, 58% peer review, 42% reach CI/CD. 72% cite time and 61% cite skills as barriers. 66% of false positives come from vendor rules. |
| [CardinalOps SIEM detection risk report, via Dark Reading](https://www.darkreading.com/analytics/enterprise-siem-blind-mitre-attack-coverage) | SIEMs ingest enough data to cover about 94% of ATT&CK techniques, yet most are blind to a majority of them. |
| [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/2025-12-09/owasp-top-10-for-agentic-applications-for-2026) | Ten agent-specific risk classes (ASI01 to ASI10), published 9 December 2025. |
| [MITRE ATLAS release v2026.09](https://www.speakeasy.com/blog/mitre-atlas-explained) | 120 techniques and 88 sub-techniques; 139 of the 208 entries carry the Agentic AI tag. |
| [postmark-mcp compromise](https://www.mintmcp.com/blog/postmark-mcp-malicious-server-email-exfiltration) | A one-line change in an MCP server BCC'd every email to an attacker. No prompt injection or model misbehavior was involved. |
| [MCP trust-boundary research](https://securityboulevard.com/2026/04/attacking-the-mcp-trust-boundary/) | A 2025 study found tool poisoning in roughly 5.5% of 1,899 public MCP servers. |
| [Anthropic, first reported AI-orchestrated espionage campaign](https://www.anthropic.com/news/disrupting-AI-espionage) | About 30 targets; AI did an estimated 80-90% of the campaign with 4-6 human decision points. |
| [Google GTIG AI Threat Tracker](https://cloud.google.com/blog/topics/threat-intelligence/threat-actor-usage-of-ai-tools) | Malware families (PROMPTFLUX, PROMPTSTEAL, PROMPTLOCK) that call LLMs during execution. |

Three structural gaps explain why a SIEM-only approach struggles. First, **identity**: an agent often acts under a user's or a service principal's identity, so logs name the human, not the agent; one practitioner reported closing an alert as a false positive for exactly this reason (anecdotal, but consistent with the architecture). Second, **telemetry**: agent, tool-call and MCP events are not emitted or collected by default, and the OpenTelemetry GenAI conventions that would standardize them are still at Development stability. Third, **content type**: tool poisoning and rug pulls live in natural-language tool descriptions and runtime behavior, which static code analysis cannot see.

The second half of the problem is that agentic authoring is promising but unproven. In the AVDA study of 92 production detections, agent-written rules matched attack techniques 99.4% of the time and were syntactically valid 95.9% of the time, but matched the reference exclusion logic only 8.9% of the time, and the generated code was never executed. ASSAY treats that gap, between plausible and verified, as the central design problem.

## Scope, audience and principles

ASSAY covers detection content and the pipeline that produces it, for two tracks: **Defend AI** (detecting attacks on and by AI agents, MCP servers and LLM infrastructure) and **Use AI** (using agents to author, test and tune detections). It is written for four readers.

| Reader | What they take from it |
| --- | --- |
| CISO | Decisions, autonomy limits, maturity levels and board-level metrics |
| Detection engineer | The Detection Hypothesis Record, validation gates and the starter catalog |
| SOC lead | Tiers, approval paths and tuning feedback loops |
| AI platform team | The telemetry contract they must emit for security to detect anything |

**Design principles.** These are ASSAY's own positions, drawn from the research, and the places they are contestable are flagged in the limitations section.

1. **Telemetry before rules.** A rule on a log source that is missing or broken is a false assurance. Every hypothesis names its telemetry prerequisites, and coverage is only counted where they are verified.
2. **Behavior before text.** Prefer signals on actions (tool-call sequences, identity use, egress, config changes) over keyword matching on prompts. Content-based signals are a secondary layer.
3. **Agents propose; tests and humans dispose.** An authoring agent never approves or deploys its own output.
4. **Executed evidence, not similarity.** A rule counts only if it fires on labeled positive logs and stays quiet on labeled negatives.
5. **Autonomy scales inversely with blast radius.** The more a detection can disrupt (block, isolate, disable), the more human control it needs.
6. **Every agent is a non-human identity.** That includes the authoring agents. Each has an owner, a scope, short-lived credentials and an expiry.
7. **Portable by default.** Detections are expressed in a SIEM-neutral form (in a vendor-neutral Detection Logic Specification, with Sigma as one output format) so that the framework survives platform changes.

**Non-goals.** ASSAY is not a prompt-injection classifier, a guardrail or prevention framework, a replacement for the OWASP and MITRE taxonomies it builds on, an incident-response playbook, or a product. It specifies how to decide what to detect and how to prove it; it does not prescribe a vendor.

## Status, conventions and terms

**Status.** This is version 0.1, a draft for public review. It is a community specification, not a standard of any standards body, and nothing in it is endorsed by NIST, ISO, OWASP, MITRE or the European Union.

**Normative language.** The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY and OPTIONAL in the requirements catalogue and conformance sections are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in all capitals, as shown here.

**Normative and informative parts.** The requirements catalogue, the conformance section and the two JSON Schemas are normative. Everything else, including every example, the starter hypotheses and the crosswalk, is informative. Lowercase "must" or "should" in informative prose explains a rationale and creates no requirement. If the parts disagree, the requirements catalogue wins over prose, and the schemas win over the YAML examples.

**Terms.**

| Term | Meaning in this document |
| --- | --- |
| Agent | A software system in which a language model chooses actions and calls tools on behalf of a person or service |
| MCP server | A Model Context Protocol server that exposes tools or data to an agent |
| Detection | A rule, query, model or correlation that raises an alert or tag from telemetry |
| Detection Hypothesis Record (DHR) | The YAML record that carries one detection's threat, telemetry needs, rule, evidence, owner and approvals |
| Detection Logic Specification (DLS) | The vendor-neutral YAML description of a detection's logic, from which adapters generate rules |
| Adapter | A component that turns a DLS into a rule for one SIEM or query language and declares what meaning it loses |
| Detection pack | A versioned set of DHRs, DLSs, fixtures and evidence bundles |
| Fixture | Labeled test events: positives, negatives and variants |
| Evidence bundle | The set of artifacts that lets a third party replay and check a detection's claims (defined under Conformance) |
| Impact tier | T-Info, T-Invest or T-Disrupt: what the detection can do when it is wrong |
| Readiness T0 to T3 | How much of the Layer 1 contract a telemetry source provides, from none (T0) to provenance and MCP lifecycle events (T3) |
| Authoring agent | An agent that drafts or changes detection content |
| Autonomy A0 to A3 | The ceiling on what an authoring agent may do without a human, set per tier in Layer 5 |
| Telemetry emitter | A platform or component that produces Layer 1 events |

## Where ASSAY fits

ASSAY does not replace existing work. Its aim is to connect that work with an engineering method for building, proving and governing detections for agentic systems. The table shows what each project contributes and what ASSAY adds on top.

| Existing work | What it contributes | What ASSAY adds |
| --- | --- | --- |
| Sigma | Portable detection rules and, since version 2.0, correlation rules | Evidence, lifecycle and governance around the rule, and a logic layer for stateful and sequence detections |
| MITRE ATLAS | AI adversary techniques and case studies | Conversion of techniques into testable hypotheses with telemetry prerequisites |
| OWASP Agentic Top 10 | A taxonomy of agentic risks | A mapping from each risk to required telemetry and a detection hypothesis |
| ATR (Agent Threat Rules) | A rule format and rules for agent threats | Validation, evidence and promotion rules around such rules |
| AI/ML DFIR detection pack | Sigma, YARA and Suricata content for AI compromise | A repeatable pipeline and telemetry check for that content |
| Detection Engineering Maturity Matrix | General detection-program maturity | Agent-specific telemetry and AI-authoring maturity |
| OpenTelemetry GenAI and OCSF | Schemas for agent telemetry | A security-oriented minimum contract with identity lineage |
| Nebulock Agentic Detection Engineering Framework (ADEF) | An MIT-licensed CLI and MCP server that wraps existing rules in per-detection journals and a five-stage lifecycle (Find, Observe, Refine, Govern, Evolve), with L0 to L4 maturity | Telemetry contract for agents, threat-to-hypothesis mapping for agentic threats, vendor-neutral logic, executed-evidence gates and a Defend AI track, none of which that project covers |
| AI Detection Engineering maturity matrix (infosecb) | A 10 by 4 matrix of how mature a team is at using AI across the detection lifecycle, from no use to autonomous pipelines | Concrete artifacts and gates a team can implement, plus detection of attacks on agents, which the matrix does not address |
| Agent-assisted pipeline practice (LimaCharlie and others) | Practitioner write-ups of sub-agents, validation gates and adversary emulation in a detection pipeline | A written, vendor-neutral specification with records, schemas and scoring that others can adopt and audit |
| Vega Detection Skills | An open, Apache-2.0 format built on the Agent Skills format that attaches triage, investigation and tuning logic to a detection; stewarded by Vega | What comes before a rule is trusted: agent telemetry, evidence gates and governed authoring autonomy. The two address different stages and can be combined |
| IAPS Agentic Security Alert Standard | A proposed reporting model for communicating agentic threats, set out in a research paper on detecting offensive cyber agents | A method for building and proving the detections that would raise such alerts, rather than the alert report format |
| OpenTIDE | Open-source threat-informed Detection-as-Code framework from the European Commission's security operations centre, with YAML objects for threat models, detection objectives and rules; its maintainers have announced a rewrite for combined agent and human use | An agent telemetry contract, an agentic threat catalogue, executed-evidence gates and autonomy tiers; ASSAY records could sit alongside or inside such a workflow |
| AARTS (Gen Digital) | An open standard for how agent platforms expose security events to runtime-protection engines | A detection-engineering method on top of such events; a mapping from the Layer 1 contract to AARTS events is future work |

**Positioning.** ASSAY is an open engineering method for building, validating and governing detections in the agentic era. It is not a rule collection, an agent-security product or a prevention framework. The ambition, not yet achieved, is that security teams build agentic detections with it, platforms emit its telemetry contract, contributors share reusable hypothesis records and test scenarios, and a detection pack validated in one SIEM can be tested and deployed in another.

**Relation to rule and skill standards.** ATR describes itself as an open detection standard for agent threats, and Vega Detection Skills describes itself as an open standard for post-match reasoning. ASSAY is neither a rule format nor a triage format: ATR rules can be inputs to an ASSAY pipeline, and a Detection Skill can be attached to a detection that ASSAY has validated. Wording that overlaps with these projects ("open standard") is avoided here; ASSAY calls itself a specification and methodology.

**Name and novelty.** An assay is a test of what a thing is worth; here, of whether a detection works. The name was chosen after a conflict check: an open-source project from Nebulock already uses the name Agentic Detection Engineering Framework and the abbreviation ADEF, and an earlier working name, OADS, was dropped for the same reason. ASSAY is also an ordinary English word, so a bare web search for it returns unrelated results; cite it as "ASSAY detection engineering". No trademark clearance has been performed. Related work exists on the lifecycle, maturity and AI-assisted authoring sides, so ASSAY does not claim to be first in this area; its claim is narrower: a combined specification covering agent telemetry, threat-to-detection mapping, vendor-neutral logic, evidence gates and governed autonomy. This survey is not exhaustive and the space moves quickly, so check for newer efforts before claiming novelty. Details of the Nebulock project come from its public pages as read on 12 November 2026.

## Framework overview

*Figure: framework overview, five layers with one feedback loop. The figure is in the published document; see Framework overview above.*

Defend AI hypotheses enter at Layer 2 once Layer 1 telemetry exists; Use AI changes how Layer 3 works. Layers 4 and 5 apply to every detection, whether a human or an agent wrote it, and what analysts learn from triage, incidents and red-team work flows back into Layer 2.

**What passes between layers.** Each layer hands the next a defined artifact, so work can be checked at every boundary. A bridge artifact, the Detection Logic Specification, sits between the hypothesis and any SIEM-specific rule.

| Stage | Consumes | Produces | Defined in |
| --- | --- | --- | --- |
| Layer 1 | Raw agent, tool, MCP, identity and egress events | Normalized events with identity lineage, plus log-health status | Telemetry contract |
| Layer 2 | Readiness levels and threat-taxonomy entries | Detection Hypothesis Record: behavior, observable, prerequisites | Detection Hypothesis Record |
| Bridge | Hypothesis record | Detection Logic Specification: fields, correlation keys, sequences, thresholds, exclusions, expected alert, tests | Detection Logic Specification |
| Layer 3 | Hypothesis record and logic specification | Backend rules from adapters, test fixtures, provenance | Layer 3 and adapters |
| Layer 4 | Rule and fixtures | Validated detection with quality scores and an evidence bundle | Layer 4 |
| Layer 5 | Validated detection | Promoted detection with owner, tier, monitoring and rollback | Layer 5 |

Because the logic specification fixes the intent, one hypothesis can be converted into different SIEM implementations without changing what it is meant to catch.

## Layer 1: Telemetry contract

No detection is possible without events that say which agent did what, on whose behalf, using which tool and credential. The contract below is the minimum every agent deployment must emit before security will count it as covered. Field names are ASSAY's own working names; the mapping column shows where they align with open schemas.

| Event class | Minimum fields | Detects (examples) | Aligns with |
| --- | --- | --- | --- |
| Agent run | agent.id, agent.name, agent.version, session.id, turn.id, owner, initiating principal | Rogue or unregistered agents, off-hours runs | OTel `invoke_agent`, `create_agent` |
| Tool call | tool.name, mcp.server, args hash (content redacted by default), result status, caller turn.id | Unexpected tool sequences, mass export, privilege changes | OTel `execute_tool`; OCSF API Activity (6003) |
| Context provenance | context.sources\[\] (URI or record id), trust level of each source | Indirect prompt injection followed by an egress tool | Working draft; no standard yet |
| MCP lifecycle | server id, package name and version, tools/list hash, description-change event | Tool poisoning, rug pulls, typosquatted servers | OTel MCP conventions (Development) |
| Identity and credential | token issuance, secret reads, OAuth grants, agent id, on-behalf-of user, credential id | Stolen agent tokens, new secrets on service principals | IdP and cloud audit logs |
| Config and memory writes | file path, actor, diff hash for MCP configs, skill files, persistent memory | Config tampering, memory poisoning | Endpoint and file events |
| Egress | destination, bytes, process or workload, agent id | Exfiltration, shadow AI, LLM API used as C2 | Proxy and flow logs |
| Human approval | what was shown, what was executed, approver | Approval fatigue, misleading summaries (ASI09) | Working draft |
| LLM gateway | model, provider, token counts, caller | LLMjacking, unapproved model use | OTel GenAI inference spans |

**Identity lineage is the one non-negotiable rule.** Every action event must carry three identifiers: the agent, the human or system it acts for, and the credential it used. Without all three, an alert cannot distinguish an agent acting within its remit from a person, and baselines built on human behavior break silently.

**Schemas.** Emit OpenTelemetry GenAI spans where your framework supports them, and normalize to OCSF at ingestion for security tooling; at least one open project already extends OCSF API Activity for agent and MCP events. Treat both as moving targets: every `gen_ai.*` attribute is currently at Development stability, and content capture is opt-in. Pin versions and keep a mapping layer so a schema change is a config change, not a rule rewrite.

**Privacy rule.** Capture metadata by default and capture prompt or response content only where a data-governance decision says so. Hashes and provenance identifiers carry most detection value without storing user content.

**Log health is part of the contract.** For each source, run these checks and alert on failure:

- Heartbeat: expected volume per agent per hour, alert on silence
- Schema conformance: required fields present and typed
- Latency: event-to-SIEM delay within an agreed bound
- Identity completeness: percentage of action events carrying all three identifiers

**Readiness levels** let you state coverage honestly. T0: none. T1: gateway or proxy logs only. T2: tool-call events with identity lineage. T3: T2 plus context provenance and MCP lifecycle events. Layer 2 uses these levels to decide which hypotheses are testable.

## Layer 2: Threat-to-detection map

This layer turns public threat taxonomies into detection hypotheses your telemetry can actually test. A hypothesis that needs telemetry you lack is not a rule to write; it is a telemetry backlog item.

**Method.**

1. **Inventory the assets:** agents, MCP servers, LLM gateways, agent-capable developer tools. Include the components agents can discover at runtime.
2. **Select threats** from the OWASP Agentic Top 10 and MITRE ATLAS that apply to those assets. Pin the ATLAS release you used; it ships monthly.
3. **State each hypothesis** as attacker behavior, the observable it produces, and the data source that shows it.
4. **Check prerequisites** against the Layer 1 readiness levels. If they are not met, log a telemetry gap instead of writing a rule.
5. **Prioritize by exposure:** agent privilege, data reach and autonomy, not by taxonomy order.
6. **Record** each result as a Detection Hypothesis Record (see that section).

The table gives ASSAY's starting hypothesis for each OWASP agentic risk. The signals are working proposals to be tuned per environment, not validated rules.

| Risk | Starting detection signal | Telemetry needed | Readiness |
| --- | --- | --- | --- |
| ASI01 Agent goal hijack | An egress or write tool is called in a turn whose context included an untrusted source, and the call does not fit the user's stated task | Tool call, context provenance | T3 |
| ASI02 Tool misuse | Tool parameters outside policy; chains of individually safe tools that end in export or privilege change | Tool call | T2 |
| ASI03 Identity and privilege abuse | New secret or certificate added to an agent's service principal; agent sign-in from a first-seen IP; shared or long-lived credentials in use | Identity and credential | T2 |
| ASI04 Agentic supply chain | New MCP server registered; tools/list or description hash changed after approval; unreviewed package version | MCP lifecycle | T3 |
| ASI05 Unexpected code execution | Agent process spawns a shell or interpreter; outbound connection from a sandbox that should be deny-by-default | Endpoint, egress | T2 |
| ASI06 Memory and context poisoning | Write to persistent memory or a retrieval store originating from an untrusted source | Config and memory writes, provenance | T3 |
| ASI07 Insecure inter-agent communication | Messages from unregistered agents; delegation outside the allowed paths | Agent run, tool call | T2 |
| ASI08 Cascading failures | Several agents deviate from baseline in the same window; sudden fan-out of calls | Agent run metrics | T2 |
| ASI09 Human-agent trust exploitation | Approved action differs from what the approval prompt displayed; rubber-stamp approval rates | Human approval | T3 |
| ASI10 Rogue agents | Agent with no owner or past expiry; activity from an unregistered agent id; sustained baseline deviation | Agent run, identity | T2 |

**Two ways to detect, and ASSAY supports both.** Per-agent behavioral baselines (tool, argument shape, call frequency, sequences) catch what policy did not anticipate, but practitioners disagree on how stable they are: the same task can yield different action sequences on each run. The alternative is to harden the sandbox and alert on boundary violations, so the boundary itself is the baseline. Use boundary rules as the high-confidence tier and baselines as a lower-confidence, tuned tier.

**Coverage is counted, not claimed.** A hypothesis is covered only when its telemetry prerequisites are verified healthy and its rule has passed Layer 4. Coverage reports show three numbers per taxonomy: hypotheses defined, hypotheses testable at current readiness, and hypotheses validated and live.

## Layer 3: Agentic authoring

Agents should draft detection content in a staged pipeline with narrow roles, not as one agent that does everything. In the AVDA study a fixed retrieve-then-generate pipeline reached about 87% of the quality of a fully agentic loop at much lower token cost, so ASSAY defaults to staged pipelines and reserves open-ended loops for hard cases.

**Pipeline stages.** Each stage has a defined input, output and permission set.

| Stage | Input | Output | Permissions |
| --- | --- | --- | --- |
| 1. Intake | Threat intel, incident write-up, taxonomy entry, red-team finding | Candidate hypothesis in Detection Hypothesis Record form | Read-only on intel; no SIEM access |
| 2. Feasibility | Hypothesis, telemetry inventory | Prerequisite check: testable now, or a telemetry gap ticket | Read-only on schema catalog and log-health data |
| 3. Draft | Hypothesis, similar existing rules, field schema | Detection logic specification, adapter output (for example Sigma or a SIEM query) and exclusions rationale | Read-only on rule repo and schema; writes only to a branch |
| 4. Test authoring | Hypothesis, rule | Labeled positive and negative events, emulation steps | Writes to test fixtures only |
| 5. Critique | Rule, tests, hypothesis | Independent review: logic gaps, evasions, noisy fields | A separate agent or model from stage 3; read-only |
| 6. Submit | Passing candidate | Pull request with provenance metadata | Can open a PR; cannot merge or deploy |

**Retrieval first.** Ground drafts in your own rule library and field schema. In AVDA, giving the model schema tools improved library and data-source selection where enabled, but field accuracy stayed low, so schema validation in Layer 4 is mandatory and not optional.

**Humans own what agents do poorly.** The same study found strong technique matching but weak exclusion logic (8.9% parity with the reference), and its authors note that engineers remain essential for environment-specific context and exclusions. ASSAY therefore requires a human to author or approve the exclusion and allowlist section of any rule that agents drafted.

**Agents must never:**

- Merge, approve or deploy their own output, or edit the validation gates that judge it
- Disable, suppress or loosen an existing production detection without a human approval on a named change
- Use production credentials; authoring agents work in a sandbox tenant with synthetic or replayed data
- Treat threat intelligence, tickets or log content as instructions; these are untrusted input (see the threat model section)
- Hold standing access; credentials are issued per task, scoped to environment and time

**Provenance on every artifact.** Each rule records the authoring model and version, the pipeline run, the inputs it was given, the human reviewer, and timestamps. This is what lets you audit, roll back and measure agent-authored rules separately from human ones.

## Layer 4: Validation gates

A rule becomes eligible for production only after it passes every gate below, and the evidence for each pass is stored with the rule. The gates exist because similarity to a reference rule is not the same as correctness: published evaluations of agent-written detections have scored similarity, and the generated code was not executed.

| Gate | Question it answers | Pass criterion (default, tune per tier) | Evidence kept |
| --- | --- | --- | --- |
| G0 Static | Is it well-formed and does it reference real fields? | Valid schema, required metadata present, every field exists in the schema catalog, no unbounded wildcards | Lint report |
| G1 Replay | Does it fire on the bad and stay quiet on the good? | Fires on all labeled positives, on none of the labeled negatives, including benign agent noise such as retries | Fixture set and result |
| G2 Emulation | Does the alert appear end to end in the real pipeline? | Emulated behavior produces an alert through ingestion, normalization and the rule engine | Run log and alert id |
| G3 Noise budget | Will it bury the SOC? | In shadow mode on production-shaped history, alert volume stays within the budget set for its tier | Volume and sample review |
| G4 Evasion review | How easily is it dodged? | Critique stage and a human reviewer record the known bypasses and accept or mitigate each | Review notes |
| G5 Regression | Does it still work next month? | Scheduled re-run keeps passing; failure opens a ticket and blocks further promotion | Run history |

**Fixtures for agent behaviors.** Positive cases for Defend AI rules are produced by scripted scenarios in an isolated sandbox: a test MCP server whose description changes after approval, a document with a planted instruction that a test agent reads, an agent service principal that gains a new secret. For host-level techniques, tools such as Atomic Red Team already map techniques to executable tests, and a CI pipeline can run the mapped test on every change and fail the build when the rule stops firing.

**Negatives matter as much as positives.** Agents retry, fan out and behave differently run to run. Include recorded benign runs, and deduplicate repeated tool calls within a short window so a retry does not double count. Expect most early false positives to come from legitimate but unusual agent workflows; the usual fix is an allowlist of tool sequences per agent role, owned by a human.

**Drift is a failure mode, not an edge case.** Cloud providers add event names, agent frameworks rename attributes, and schemas such as `gen_ai.*` are still changing. G5 runs on a schedule, and any telemetry schema change triggers a re-run of every rule that depends on it.

**The noise budget is a policy decision.** Set it per tier: informational rules can be loose, anything that pages a human needs a tight budget, and anything that triggers a response action needs the tightest. Record the expected alerts per day on the rule so later tuning has a baseline.

**Scoring informs promotion; the gates are a floor.** A rule that misses a labeled positive or fires on a labeled negative cannot proceed, but passing replay does not prove effectiveness: a rule that catches every artificial scenario can still fail against real-world variation. Promotion decisions therefore use the scores below, stored in the rule's evidence bundle.

| Measure | Definition | Note |
| --- | --- | --- |
| Recall | Share of positives detected | Report per attack variant, not only overall |
| Precision | Share of alerts that are true | Measured on shadow-mode, production-shaped data |
| False-positive rate | False alerts per day, or per 1,000 agent sessions | Compared with the tier's noise budget |
| Detection latency | Time from event to alert | Measured end to end in G2 |
| Variant coverage | Share of defined variants detected: permuted order, padded steps, alternate tools, renamed fields, delegated runs | Variants are listed in the logic specification |
| Evasion resistance | Share of reviewed bypasses mitigated or explicitly accepted | From G4 |
| Dataset quality | Size, source, labeling method, age, and whether data is synthetic or recorded | Shown beside every score |
| Uncertainty | Confidence interval on recall and precision where the sample supports one; otherwise the label "insufficient sample" | Never a bare point estimate from a handful of cases |

ASSAY does not set numeric thresholds, because the right values depend on tier and environment; each organization sets them per tier and records them.

**Two evidence statuses.** A rule is *controlled-tested* when it has passed G0 to G5 on fixtures and shadow data. It is *production-proven* only after it has operated live for a defined period with measured precision and analyst-confirmed outcomes, reviewed at its review date. Coverage reports show the two counts separately, and only controlled-tested detections count toward the validated-coverage metric until proven otherwise.

## Layer 5: Governed deployment

The amount of autonomy an authoring agent gets is set by what the detection can do when it is wrong, not by how confident the agent is. ASSAY sorts every detection into one of three impact tiers and attaches approval rules to the tier. There is no recognized industry standard for safe autonomy in detection engineering yet, so these rules are ASSAY's proposal and should be adjusted to your risk appetite.

| Impact tier | What the detection does | Who may promote it | Extra requirements |
| --- | --- | --- | --- |
| T-Info | Adds visibility: tags, enrichment, dashboards, low-severity alerts nobody is paged for | Pipeline, after gates G0 to G3, with a human notified | Shadow period; automatic rollback on volume spike |
| T-Invest | Pages an analyst or opens a case | A named human reviewer, always | Shadow period; owner and runbook recorded on the rule |
| T-Disrupt | Triggers or recommends a response: isolate a host, disable an account, revoke a token, quarantine content | A named human approver plus the response owner | Blast-radius analysis; explicit sign-off for each action type; kill switch tested |

**Authoring autonomy levels.** These cap what the pipeline may do for your organization overall.

| Level | Agent may | Typical stage |
| --- | --- | --- |
| A0 Advisory | Draft rules and tests in a scratch space; humans copy what they want | Starting out |
| A1 Branch and PR | Open pull requests with provenance; humans review every one | Default for most teams |
| A2 Bounded promotion | Auto-promote T-Info rules that pass all gates | Mature pipeline with trusted fixtures |
| A3 Supervised tuning | Propose and apply tightening changes to T-Info and T-Invest rules; loosening or suppression still needs a human | Only after a sustained clean record at A2 |

No level lets an agent self-deploy a T-Disrupt detection or approve its own change.

**Operating rules.**

- **Separation of duties:** the identity that writes a rule cannot be the identity that approves or deploys it; enforce with repository protections.
- **Provenance in the artifact:** model and version, pipeline run, reviewer, timestamps and tenant scope travel with the rule.
- **Post-deployment watch:** monitor alert-volume spikes, silence, false-positive reports and cross-tenant leakage for every agent-authored rule, and roll back automatically on breach.
- **Rollback is rehearsed:** every promotion has a one-step revert, and the time to revert is measured.
- **Short-lived credentials:** deployment access is issued per change, scoped to environment and time, and logged like any privileged identity.
- **Pipeline kill switch:** one control halts all agent promotions, tested on a schedule.
- **Multi-tenant providers:** segregate by tenant, require dual approval where regulation demands it, and keep immutable logs of agent actions.

## Use AI track: measuring agent-authored detections

The Use AI track needs its own measurement model, because an agent-written rule can look correct and still be wrong, noisy or quietly blind. The methods below are ASSAY proposals; the published evidence base is thin, so treat them as hypotheses to test in your own pipeline.

| Question | ASSAY method |
| --- | --- |
| How is generated detection quality measured? | Use the Layer 4 scores, tagged by provenance, so agent-authored and human-authored rules are compared on identical measures, with sample sizes shown. Score executed outcomes, not similarity to a reference rule. |
| How are hallucinated fields caught? | G0 checks every field and enumerated value against the schema catalog, then confirms each field is actually populated in sampled real events. A field that exists in the schema but is empty in your data never fires, so such a rule fails. |
| How are exclusions that hide malicious behavior caught? | Every exclusion needs an owner, a narrow scope, an expiry and a counter-test: a positive fixture near the exclusion's scope that must still fire. Run all positives with exclusions enabled and fail the rule if recall drops. Wildcard, whole-agent and whole-tool allowlists go to human review, and any exclusion change raises an alert. |
| How is the authoring agent kept from learning wrong patterns from noisy historical rules? | Curate the retrieval corpus: include only rules with measured precision and a live or validated status, exclude retired, noisy or unreviewed rules, and label vendor content by origin. Version the corpus and re-run the benchmark after every corpus change. |
| How is an AI-written detection compared with a human-written one? | Paired evaluation: for hypotheses that have both, score each on the same fixtures and shadow data, add a blind logic review by a second engineer, and track reviewer edit effort and time to live. Do not generalize from a handful of pairs. |

**Keep a held-out benchmark.** Maintain a private set of hypotheses with reference detections and executable fixtures, and re-run it whenever the authoring model, prompts, tools or retrieval corpus change. A change that lowers benchmark results does not go into the pipeline. Similarity scores alone are not enough, since a rule can resemble a reference closely and still behave differently.

**Autonomy follows the evidence.** Raise a pipeline from one authoring autonomy level to the next only when agent-authored precision and recall are no worse than the human baseline over a sustained, sufficiently large sample, and lower it when they fall.

## The Detection Hypothesis Record

The Detection Hypothesis Record (DHR) is ASSAY's portable unit of work: one YAML file per hypothesis that carries the threat, the telemetry it needs, the rule, the evidence that it works, and who approved it. It sits beside the Sigma rule in the repository and is what agents produce at intake and what reviewers sign.

| Section | Purpose | Required |
| --- | --- | --- |
| id, title, version, status, owner | Identity and lifecycle (`draft`, `testable`, `validated`, `live`, `retired`) | Yes |
| track, tier | Defend AI or Use AI; impact tier T-Info, T-Invest or T-Disrupt | Yes |
| threat | OWASP ASI id, ATLAS technique id with the pinned release, ATT&CK id where relevant | Yes |
| hypothesis | Attacker behavior, the observable it produces, the data source | Yes |
| prerequisites | Telemetry classes and minimum readiness level | Yes |
| rule | Path to the Sigma-compatible rule and any backend conversions | Yes once drafted |
| exclusions | Allowlists and known-benign patterns; human-owned | Yes if the rule has any |
| tests | Positive and negative fixtures, emulation scenario, noise budget | Yes before `validated` |
| response | Runbook link and any action the detection can trigger | Yes for T-Invest and T-Disrupt |
| provenance | Authoring model and version, pipeline run, reviewer, timestamps | Yes |
| review | Next review date and retirement condition | Yes |

A minimal example for an MCP tool-description change (illustrative; verify technique ids against the release you pin):

```yaml
id: dhr-asi04-0001
title: MCP server tool description changed after approval
version: 1
status: testable
owner: detection-engineering
track: defend-ai
tier: t-invest
threat:
  owasp_asi: ASI04
  atlas: { id: AML.T0110, release: v2026.09 }
hypothesis:
  behavior: A previously approved MCP server publishes a changed tool description or schema.
  observable: tools/list hash differs from the approved hash with no linked change.
  data_source: mcp_lifecycle
prerequisites:
  telemetry: [mcp_lifecycle]
  min_readiness: T3
rule:
  path: rules/mcp/tool_description_changed.yml
exclusions:
  owner: detection-engineering
  notes: Approved changes carry a change reference and are filtered.
tests:
  positives: fixtures/mcp/description_change_positive.json
  negatives: fixtures/mcp/description_change_approved.json
  emulation: scenarios/mcp_rug_pull_sandbox
  noise_budget_per_day: 2
response:
  runbook: runbooks/mcp-description-change.md
  action: none
provenance:
  authored_by: { model: example-model, run: run-0001 }
  reviewed_by: analyst-a
review:
  next: 2027-02-11
```

The record wraps the detection logic with its evidence. The logic itself is described once, in a vendor-neutral Detection Logic Specification (next section), and each SIEM rule, including a Sigma rule, is an adapter output generated from it. The example above references a Sigma file because its logic is a single event condition; richer detections reference the logic specification instead. ASSAY adds custom `logsource` categories for the Layer 1 event classes (for example `mcp_lifecycle`) so adapters share one field vocabulary.

**Lifecycle.** A DHR moves `draft` to `testable` when Layer 1 prerequisites are met, to `validated` when it passes G0 to G5, to `live` when promotion is approved for its tier, and to `retired` when its retirement condition is met. Status is changed by the pipeline, never by hand-editing the file.

## Detection Logic Specification

The Detection Logic Specification (DLS) is the vendor-neutral description of detection logic that sits between the hypothesis record and any SIEM-specific rule. It fixes what the detection means (fields, correlation keys, sequences, thresholds, exclusions and expected output), so each backend rule is a translation of the same intent and not a reinterpretation. Sigma is one output format among several: many agentic detections need multi-event correlation, delegation chains, stateful behavior and cross-source sequences that a single-event rule cannot express cleanly. Sigma 2.0 added correlation rules, which covers part of this; the DLS keeps the full intent where a backend cannot.

| Element | What it defines | Example for a read-then-export detection |
| --- | --- | --- |
| Inputs | Event classes and the required fields with their types, from the Layer 1 contract | tool\_call with agent.id, session.id, tool.category, data.classification, destination.approved |
| Correlation keys | The fields that join events into one subject | agent.id plus session.id; parent\_agent.id for delegation |
| Sequence and window | The steps, whether order matters, and the time bound | Read of sensitive data, then send to an unapproved destination, within one session and a stated window |
| Thresholds and aggregation | Counts, volumes or distinct values that must be exceeded | Volume read above a limit derived from the baseline |
| Baseline reference | How normal is defined: sandbox boundary, or per-agent profile with lookback and minimum history | Boundary mode: any send to an unapproved destination breaches it |
| Delegation handling | How chains are attributed: root principal, chain depth, allowed delegation paths | Attribute to the root principal; alert on paths not on the allowlist |
| Exclusions | Scoped, owned, expiring allowlists, each with a counter-test | A named support agent may send to one named CRM domain |
| Missing-field behavior | What the logic does when a required field is absent: skip, downgrade, or alert on a telemetry gap | Alert on telemetry gap |
| Expected alert | Severity, subject, evidence events and the hypothesis record id | Subject is the agent and the principal it acts for |
| Tests | Fixtures and scenarios, including variants | Positives, benign runs, permuted and padded sequences |

**Illustrative logic specification.** The schema is a draft and the values are examples only.

```yaml
dls: "0.1"
dhr: dhr-asi02-0005
inputs:
  - class: tool_call
    fields: [agent.id, session.id, principal.on_behalf_of, tool.category, data.classification, destination.domain, destination.approved]
correlate:
  by: [agent.id, session.id]
logic:
  sequence:
    - step: read_sensitive
      where: { tool.category: read, data.classification: [confidential, restricted] }
    - step: send_external
      where: { tool.category: send, destination.approved: false }
  order: strict
  window: 10m
baseline:
  mode: boundary
exclusions:
  - id: ex-1
    owner: detection-engineering
    scope: { agent.role: support-triage, destination.domain: crm.example.com }
    expires: 2027-05-12
    counter_test: fixtures/ex-1-other-destinations-still-detected.json
on_missing_field: alert_telemetry_gap
output:
  severity: high
  subject: [agent.id, principal.on_behalf_of]
  evidence: [read_sensitive, send_external]
tests:
  positives: fixtures/read_export_positive.json
  negatives: fixtures/read_export_benign.json
  variants: fixtures/read_export_variants.json
```

**Variable sequences.** Agents produce different event orders for the same intent. Express a requirement as an unordered set of behaviors within a window wherever order is not security-relevant, and require order only where it is (a read before a send). Every specification ships variant fixtures: permuted order, padded steps, alternate tools, renamed fields and delegated runs.

**Adapters.** Each target platform (for example Sentinel, Splunk, Elastic, QRadar and Sigma) gets an adapter: a documented mapping from DLS elements to that platform's constructs, a field-mapping table to its schema, and an explicit statement of what it cannot express. A rule produced by an adapter must declare any lost semantics, such as no native sequence support, and the compensating control, for example a scheduled correlation query or a streaming stage. Adapters are generated by the authoring pipeline and validated at Layer 4 like any other rule.

## Machine-readable schemas

The Detection Hypothesis Record and the Detection Logic Specification each have a JSON Schema (draft 2020-12) so that records can be checked in CI before any gate runs. The two example records in this document, dhr-asi04-0001 and the logic specification for dhr-asi02-0005, were extracted from this document and validated against these schemas, and twelve deliberately broken records were rejected, including an exclusion with no counter-test, a specification with no missing-field behavior, a record marked validated without tests, and an unknown OWASP identifier. Two conditional rules are enforced: a T-Invest or T-Disrupt record needs a response section, and a validated or live record needs a rule, tests and a named reviewer. Fields that begin with x- are reserved for extensions; any other unknown field is rejected, so a misspelled field cannot pass silently. Write the logic specification version as a string (dls: "0.1") so it is not read as a number. Validation shows a record is well formed, not that its logic is right; that is the job of Layer 4. The $id values are placeholders until a repository exists, and the schemas are version 0.1 and will change with the field names in Layer 1.

The records are written in YAML. Many YAML loaders turn an unquoted date such as 2027-02-11 into a date object, so a validator should load dates as plain strings or the format check will fail for a correct record.

**DHR schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/dhr-0.1.json",
  "title": "Detection Hypothesis Record (DHR) v0.1",
  "type": "object",
  "required": ["id", "title", "version", "status", "owner", "track", "tier", "threat", "hypothesis", "prerequisites", "provenance", "review"],
  "properties": {
    "id": { "type": "string", "pattern": "^dhr-[a-z0-9]+-[0-9]{4}$" },
    "title": { "type": "string", "minLength": 5 },
    "version": { "type": "integer", "minimum": 1 },
    "status": { "enum": ["draft", "testable", "validated", "live", "retired"] },
    "owner": { "type": "string", "minLength": 1 },
    "track": { "enum": ["defend-ai", "use-ai"] },
    "tier": { "enum": ["t-info", "t-invest", "t-disrupt"] },
    "threat": {
      "type": "object",
      "required": ["owasp_asi"],
      "properties": {
        "owasp_asi": { "oneOf": [{ "$ref": "#/$defs/asi" }, { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/asi" } }] },
        "atlas": { "oneOf": [{ "$ref": "#/$defs/atlas" }, { "type": "array", "items": { "$ref": "#/$defs/atlas" } }] },
        "attack": { "type": "array", "items": { "type": "string", "pattern": "^T[0-9]{4}(\\.[0-9]{3})?$" } }
      },
      "additionalProperties": false
    },
    "hypothesis": {
      "type": "object",
      "required": ["behavior", "observable", "data_source"],
      "properties": {
        "behavior": { "type": "string", "minLength": 10 },
        "observable": { "type": "string", "minLength": 10 },
        "data_source": { "type": "string" }
      },
      "additionalProperties": false
    },
    "prerequisites": {
      "type": "object",
      "required": ["telemetry", "min_readiness"],
      "properties": {
        "telemetry": { "type": "array", "minItems": 1, "items": { "type": "string" } },
        "min_readiness": { "enum": ["T0", "T1", "T2", "T3"] }
      },
      "additionalProperties": false
    },
    "rule": {
      "type": "object",
      "required": ["path"],
      "properties": { "path": { "type": "string" }, "backends": { "type": "array", "items": { "type": "string" } } },
      "additionalProperties": false
    },
    "exclusions": {
      "type": "object",
      "required": ["owner"],
      "properties": { "owner": { "type": "string" }, "notes": { "type": "string" } },
      "additionalProperties": false
    },
    "tests": {
      "type": "object",
      "required": ["positives", "negatives"],
      "properties": {
        "positives": { "$ref": "#/$defs/paths" },
        "negatives": { "$ref": "#/$defs/paths" },
        "variants": { "$ref": "#/$defs/paths" },
        "emulation": { "type": "string" },
        "noise_budget_per_day": { "type": "number", "minimum": 0 }
      },
      "additionalProperties": false
    },
    "response": {
      "type": "object",
      "required": ["runbook", "action"],
      "properties": { "runbook": { "type": "string" }, "action": { "type": "string" } },
      "additionalProperties": false
    },
    "provenance": {
      "type": "object",
      "required": ["authored_by"],
      "properties": {
        "authored_by": {
          "type": "object",
          "minProperties": 1,
          "properties": { "model": { "type": "string" }, "run": { "type": "string" }, "human": { "type": "string" } },
          "additionalProperties": false
        },
        "reviewed_by": { "type": "string" }
      },
      "additionalProperties": false
    },
    "review": {
      "type": "object",
      "required": ["next"],
      "properties": { "next": { "type": "string", "format": "date" }, "retire_when": { "type": "string" } },
      "additionalProperties": false
    }
  },
  "patternProperties": { "^x-": {} },
  "additionalProperties": false,
  "allOf": [
    { "if": { "properties": { "status": { "enum": ["validated", "live"] } }, "required": ["status"] }, "then": { "required": ["rule", "tests", "provenance"], "properties": { "provenance": { "required": ["authored_by", "reviewed_by"] } } } },
    { "if": { "properties": { "tier": { "enum": ["t-invest", "t-disrupt"] } }, "required": ["tier"] }, "then": { "required": ["response"] } }
  ],
  "$defs": {
    "asi": { "type": "string", "pattern": "^ASI(0[1-9]|10)$" },
    "atlas": {
      "type": "object",
      "required": ["id", "release"],
      "properties": { "id": { "type": "string", "pattern": "^AML\\.(T|CS)[0-9]{4}(\\.[0-9]{3})?$" }, "release": { "type": "string" } },
      "additionalProperties": false
    },
    "paths": { "oneOf": [{ "type": "string" }, { "type": "array", "minItems": 1, "items": { "type": "string" } }] }
  }
}
```

**DLS schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/dls-0.1.json",
  "title": "Detection Logic Specification (DLS) v0.1",
  "type": "object",
  "required": ["dls", "dhr", "inputs", "correlate", "logic", "on_missing_field", "output", "tests"],
  "properties": {
    "dls": { "const": "0.1" },
    "dhr": { "type": "string", "pattern": "^dhr-[a-z0-9]+-[0-9]{4}$" },
    "inputs": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["class", "fields"],
        "properties": { "id": { "type": "string" }, "class": { "type": "string" }, "fields": { "type": "array", "minItems": 1, "items": { "type": "string" } } },
        "additionalProperties": false
      }
    },
    "correlate": {
      "type": "object",
      "required": ["by"],
      "properties": { "by": { "type": "array", "minItems": 1, "items": { "type": "string" } } },
      "additionalProperties": false
    },
    "logic": {
      "type": "object",
      "minProperties": 1,
      "properties": {
        "sequence": {
          "type": "array",
          "minItems": 2,
          "items": { "type": "object", "required": ["step", "where"], "properties": { "step": { "type": "string" }, "where": { "type": "object", "minProperties": 1 } }, "additionalProperties": false }
        },
        "order": { "enum": ["strict", "any"] },
        "window": { "type": "string", "pattern": "^[0-9]+(s|m|h|d)$" },
        "threshold": {
          "type": "object",
          "required": ["count", "window"],
          "properties": { "count": { "type": "integer", "minimum": 1 }, "window": { "type": "string", "pattern": "^[0-9]+(s|m|h|d)$" }, "distinct": { "type": "string" } },
          "additionalProperties": false
        }
      },
      "dependentRequired": { "sequence": ["order", "window"] },
      "additionalProperties": false
    },
    "baseline": {
      "type": "object",
      "required": ["mode"],
      "properties": {
        "mode": { "enum": ["boundary", "profile"] },
        "lookback": { "type": "string", "pattern": "^[0-9]+(h|d)$" },
        "min_history": { "type": "string", "pattern": "^[0-9]+(h|d)$" }
      },
      "if": { "properties": { "mode": { "const": "profile" } }, "required": ["mode"] },
      "then": { "required": ["lookback", "min_history"] },
      "additionalProperties": false
    },
    "delegation": {
      "type": "object",
      "properties": { "attribute_to": { "enum": ["root_principal", "agent", "both"] }, "max_depth": { "type": "integer", "minimum": 1 }, "allowed_paths": { "type": "array", "items": { "type": "string" } } },
      "additionalProperties": false
    },
    "exclusions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "owner", "scope", "expires", "counter_test"],
        "properties": {
          "id": { "type": "string" },
          "owner": { "type": "string" },
          "scope": { "type": "object", "minProperties": 1 },
          "expires": { "type": "string", "format": "date" },
          "counter_test": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "on_missing_field": { "enum": ["alert_telemetry_gap", "downgrade", "skip"] },
    "output": {
      "type": "object",
      "required": ["severity", "subject", "evidence"],
      "properties": {
        "severity": { "enum": ["info", "low", "medium", "high", "critical"] },
        "subject": { "oneOf": [{ "type": "string" }, { "type": "array", "minItems": 1, "items": { "type": "string" } }] },
        "evidence": { "type": "array", "minItems": 1, "items": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "tests": {
      "type": "object",
      "required": ["positives", "negatives", "variants"],
      "properties": {
        "positives": { "$ref": "#/$defs/paths" },
        "negatives": { "$ref": "#/$defs/paths" },
        "variants": { "$ref": "#/$defs/paths" }
      },
      "additionalProperties": false
    }
  },
  "patternProperties": { "^x-": {} },
  "additionalProperties": false,
  "$defs": {
    "paths": { "oneOf": [{ "type": "string" }, { "type": "array", "minItems": 1, "items": { "type": "string" } }] }
  }
}
```

## Requirements catalogue (normative)

Each requirement has a stable identifier, applies to one or more classes (E = telemetry emitter, P = detection pack, A = adapter, O = organization or program), and names the evidence a reviewer checks. Identifiers are never reused. Requirements restate rules described in the layers above; the layer text explains why.

| ID | Requirement | Applies to | Evidence |
| --- | --- | --- | --- |
| TEL-01 | An emitter MUST produce each Layer 1 event class it claims to cover, with at least the minimum fields in the Layer 1 table. | E | Sample events checked against the field list |
| TEL-02 | Every action event MUST carry identity lineage, so that an action can be traced to the agent, session, owner, initiating principal and credential involved. | E | Lineage completeness check over sample events |
| TEL-03 | An emitter MUST NOT record prompt or tool-argument content by default; arguments SHOULD be recorded as hashes unless the organization has enabled content capture. | E | Emitter configuration and sample events |
| TEL-04 | An emitter MUST state the readiness level (T0 to T3) it achieves for each event class. | E | Readiness statement |
| LOG-01 | The organization MUST run log-health checks on every source that a live detection depends on. | O | Health-check configuration and recent results |
| LOG-02 | A detection whose required telemetry is missing or degraded MUST NOT count toward coverage, and its DLS MUST declare an on\_missing\_field behavior. | P, O | DLS field; coverage report |
| HYP-01 | Every detection MUST have a DHR that is valid against the DHR schema. | P | Schema validation result |
| HYP-02 | A DHR MUST state the threat it addresses, and MUST pin the ATLAS release when it cites an ATLAS technique. | P | DHR threat block |
| HYP-03 | A DHR with status validated or live MUST include its rule, its tests and the name of a reviewer. | P | DHR content; schema conditional rules |
| HYP-04 | A DHR with tier t-invest or t-disrupt MUST include a response block naming a runbook. | P | DHR response block |
| HYP-05 | DHR identifiers MUST be unique and stable, and MUST NOT be reused after a record is retired. | P | Repository history |
| LOGIC-01 | Every exclusion in a DLS MUST have an identifier, an owner, a scope, an expiry date and a counter-test. | P | DLS exclusions block |
| LOGIC-02 | A DLS MUST include positive tests, negative tests and variant tests. | P | DLS tests block; fixture set |
| LOGIC-03 | An adapter MUST document its field mapping and every semantic it cannot express, and MUST NOT drop logic silently. | A | Adapter documentation; lost-semantics report per generated rule |
| VAL-01 | A detection MUST pass gates G0 to G3 before it is promoted to any live status, and the evidence named for each gate MUST be kept. | P, O | Gate results |
| VAL-02 | Coverage MUST be reported only for detections that have reached validated status. | O | Coverage report |
| VAL-03 | The organization MUST set a noise budget per impact tier and record it; this specification sets no numeric value. | O | Recorded budgets |
| VAL-04 | A scheduled regression run (G5) MUST exist for every live detection; a failure MUST open a ticket and block further promotion. | O | Run history |
| VAL-05 | Evidence claims MUST distinguish controlled-tested from production-proven. | P, O | DHR evidence status |
| AUT-01 | Each authoring agent MUST operate at a recorded autonomy level and MUST NOT exceed the ceiling the impact tier allows. | O | Autonomy register |
| AUT-02 | A human MUST author or approve the exclusion and allowlist section of any detection an agent drafted. | O | Review record |
| AUT-03 | T-Invest promotion MUST have a named human reviewer. T-Disrupt promotion MUST have a named human approver and the response owner, a blast-radius analysis, and a tested kill switch. | O | Approval records |
| AUT-04 | T-Info promotion by the pipeline MUST follow gates G0 to G3, a shadow period and a human notification, with automatic rollback on a volume spike. | O | Pipeline log |
| GOV-01 | Every live detection MUST have a named owner and a next-review date. | P, O | DHR owner and review fields |
| SEC-01 | The authoring pipeline MUST emit Layer 1 telemetry and MUST be covered by its own detection hypotheses. | O | Pipeline telemetry; hypothesis list |
| SEC-02 | The pipeline MUST fail closed: if a gate cannot run or its evidence is missing, the detection MUST NOT be promoted. | O | Pipeline configuration; failure test |

## Conformance (normative)

Conformance is claimed for one class at a time, against a named version of this specification. In version 0.1 every claim is a self-assessment; no certification body or test suite exists yet, and the claim wording must not imply otherwise.

| Class | Requirements that MUST be met | What a reviewer checks |
| --- | --- | --- |
| Telemetry emitter | TEL-01 to TEL-04 | Sample events and the readiness statement |
| Detection pack | HYP-01 to HYP-05, LOGIC-01, LOGIC-02, VAL-01, VAL-05, GOV-01, LOG-02 (the declaration) | Every DHR and DLS validates; every promoted detection has a replayable evidence bundle |
| Adapter | LOGIC-03 | Mapping document; lost-semantics report; shared test scenarios, once published |
| Organization or program | LOG-01, LOG-02, VAL-01 to VAL-05, AUT-01 to AUT-04, GOV-01, SEC-01, SEC-02 | Records named in the catalogue, sampled |

**Evidence bundle.** For each promoted detection the bundle MUST contain: the DHR and DLS files; the adapter output and its lost-semantics report; the fixture set (positives, negatives and variants); the result of each gate with a run identifier; the reviewer and approver records the tier requires; the versions of the schemas, adapters and tools used; and instructions to replay the fixtures. A third party can then rerun the gates without access to the author's environment.

**Claim wording.** A claim reads "conformant with ASSAY version X as a detection pack" (or emitter, adapter, organization), lists any requirement it does not meet, and is never worded as endorsement by the project.

## Roles and responsibilities (informative)

R = does the work, A = accountable (one per row), C = consulted, I = informed. The approver is a named person for each tier, not a group; for T-Disrupt the response owner also signs.

| Activity | CISO | Detection engineering lead | SOC lead | AI platform owner | Authoring-agent owner | Approver |
| --- | --- | --- | --- | --- | --- | --- |
| Set risk appetite, impact tiers and noise budgets | A | R | C | I | I | I |
| Emit the telemetry contract and keep log health | I | C | I | A/R | C | I |
| Write and own hypothesis records | I | A | C | C | R | I |
| Approve exclusions and allowlists | I | A/R | C | C | I | C |
| Promote T-Info detections | I | A | I | I | R | I |
| Promote T-Invest detections | I | R | C | I | I | A |
| Promote T-Disrupt detections | I | R | C | C | I | A |
| Run regression and noise review | I | A | R | C | R | I |
| Operate and secure the authoring pipeline | I | C | I | C | A/R | I |

## Worked example (illustrative)

This walk-through follows one detection through the artifacts. It describes structure only; it reports no measurements, and a real pack would attach real results.

1. **Hypothesis.** An agent that reads sensitive data and then calls an external-sending tool within a short window may be exfiltrating that data (OWASP ASI02, tool misuse). The DHR names the threat, the telemetry it needs (tool-call events with identity lineage) and its minimum readiness, and sets the tier.
2. **Logic.** The DLS expresses the detection once: a read-sensitive step followed by a send-external step, strict order, ten-minute window, correlated on the agent session, with a boundary baseline, one owned and expiring exclusion, and an on\_missing\_field behavior that raises a telemetry-gap alert instead of staying silent.
3. **Adapter output.** An adapter for a chosen SIEM generates the rule. If that SIEM cannot enforce strict order inside a window, the adapter must say so in its lost-semantics report, for example that ordering was relaxed to co-occurrence, so reviewers know the rule is broader than the specification.
4. **Fixtures.** Positives: the sequence inside the window. Negatives: a read with no send, a send before the read, a send after the window closes, and benign agent retries. Variants: renamed tools, and interleaved events from other sessions that must not be correlated.
5. **Gates.** G0 lints the DHR, DLS and generated rule. G1 replays the fixtures. G2 emulates the behavior end to end and records the alert. G3 runs shadow mode against history. G4 records known bypasses, such as splitting the read and the send across sessions. G5 schedules the replay. Each result goes in the evidence bundle.
6. **Promotion.** Because the detection pages an analyst, it is T-Invest: a named human reviews the evidence and the exclusions before the status moves to live.

## Maturity model and CISO metrics

ASSAY defines five levels so that an organization can state where it is and what the next step costs. The levels are ASSAY's own and deliberately narrow; they complement general models such as the Detection Engineering Maturity Matrix rather than replace them.

| Level | Name | What is true | Evidence to show |
| --- | --- | --- | --- |
| 0 | Unaware | No inventory of agents or MCP servers; no agent telemetry | None |
| 1 | Visible | Agents and MCP servers inventoried with owners; gateway or proxy logs collected (T1); a few ad-hoc rules | Inventory, log-source list |
| 2 | Detectable | Tool-call events with identity lineage (T2); Detection Hypothesis Records for the highest-exposure risks; rules in Git with peer review | DHRs, repo history |
| 3 | Verified | Validation gates G0 to G5 in CI; shadow mode; coverage counted only when validated; authoring agents at A1 | Gate results, coverage report |
| 4 | Adaptive | Provenance and MCP lifecycle telemetry (T3); scheduled emulation; triage outcomes feed tuning; bounded autonomy (A2 to A3) with rehearsed rollback | Regression history, tuning log, rollback drills |

**Metrics a CISO should track.** ASSAY gives definitions, not targets: baseline first, then set targets against your risk appetite.

| Metric | Definition | Why it matters |
| --- | --- | --- |
| Agent inventory coverage | Share of discovered agents and MCP servers registered with an owner and expiry | Unregistered agents are the first rogue-agent signal |
| Identity lineage completeness | Share of agent action events carrying agent, principal and credential ids | Without it, baselines and attribution fail |
| Telemetry readiness | Share of agents at T2 or better, and at T3 | Caps what you can detect |
| Validated coverage | Hypotheses validated and live, divided by hypotheses applicable to your assets, per taxonomy | Replaces rule counts and ATT&CK heatmaps with something provable |
| Hypothesis-to-live time | Median days from intake to a live, validated detection | Shows whether the pipeline helps or hinders |
| Regression pass rate | Share of live rules passing their scheduled G5 run | Early warning of silent breakage |
| Noise | Alerts per rule per day against budget; share of false positives that come from vendor rules | Where tuning effort should go |
| Agent-authored precision | False-positive rate of agent-authored rules compared with human-authored | Evidence for raising or lowering autonomy |
| Time to rollback | Median time to revert a bad promotion | Proves the safety net works |
| Emulated detection latency | Time from emulated behavior to alert | A practical measure of end-to-end speed |

Report the first four to the board; use the rest to run the program.

## Adoption roadmap

*Figure: adoption roadmap, three phases with three gates. The figure is in the published document.*

Phases are equal bands, not drawn to scale; a gate must pass before the next phase starts. A lean team can stop after Phase 2 and still have visibility plus four drafted hypotheses with replay tests. A team already running detection-as-code should start at Phase 2 and compress Phase 3, since it already has CI. In both cases keep authoring autonomy at A1 until the pipeline has a clean record.

## Threat model of the framework itself

An authoring pipeline is a privileged agent system, so it faces the same attacks it is meant to detect, and attackers have already shown they will target AI-based defenses: Google documented a reverse shell, FRUITSHELL, that carries hard-coded prompts meant to confuse LLM-powered analysis. ASSAY therefore applies its own rules to itself, and the pipeline emits Layer 1 telemetry and is covered by its own hypotheses.

| Threat | How it hits the pipeline | Control |
| --- | --- | --- |
| Injection through threat intel, tickets or advisories | Hidden instructions in a report push the agent to write a permissive rule or add an exclusion | Treat all inputs as untrusted data; intake stage has no tool or SIEM access; independent critique stage; human approval of exclusions |
| Fixture poisoning | Test data is shaped so a weak rule passes its gates | Fixtures from controlled sources; negatives taken from recorded production runs; human review of fixtures |
| Attacks aimed at AI-based analysis | Malware or content with prompts designed to mislead an LLM verdict | Deterministic rules at the core; an LLM verdict is never the only control |
| Authoring-agent over-privilege or token theft | A stolen or over-scoped agent token can change production detections | Sandbox tenant, per-task short-lived credentials, no production credentials, owner and expiry on each agent |
| Suppression by persuasion | The agent is talked into loosening or disabling a detection | Loosening needs a named human approval; alert on rule edits, disables and exclusion changes |
| Gate tampering | The agent edits the tests or validation code that judge it | Gates and fixtures under separate ownership; the authoring identity has no write access to them |
| Tool and MCP supply chain of the pipeline | A poisoned MCP server or library used by the authoring agent | Inventory the pipeline's own tools; pin tool-description hashes; apply the same ASI04 hypotheses to it |
| Hallucinated fields and false assurance | A rule references fields that do not exist, or looks right but never fires | G0 schema checks and G2 end-to-end emulation |
| Reviewer approval fatigue | Agent-written pull-request summaries hide what a change really does | Reviewers see the raw diff; summaries are supplementary only (ASI09 applied to your own reviewers) |
| Cross-tenant leakage | A rule or context from one tenant reaches another | Tenant-scoped credentials, repositories and fixtures; leakage monitoring after deployment |

**Fail closed.** If the pipeline cannot reach its validation gates or its log-health checks, promotions pause; they do not proceed unvalidated.

## Starter hypothesis catalog

These twelve hypotheses are ASSAY's seed catalog for the Defend AI track. Each is a proposal to be written as a Detection Hypothesis Record, validated through Layer 4 and tuned to your environment; none is a validated rule. Technique ids come from public ATLAS case studies and should be re-checked against the release you pin.

| ID | Hypothesis | Risk | Related technique | Readiness |
| --- | --- | --- | --- | --- |
| H01 | MCP tool description or schema changes after approval (rug pull) | ASI04 | ATLAS AML.T0110 AI Agent Tool Poisoning | T3 |
| H02 | New or unregistered MCP server added to an agent or developer tool | ASI04 | ATLAS AML.T0104 Publish Poisoned AI Agent Tool (supply side) | T3 |
| H03 | MCP package updated to a version outside the reviewed set, or a package whose name resembles an approved one | ASI04 | postmark-mcp case study, AML.CS0053 | T3 |
| H04 | Egress or write tool called in a turn whose context included an untrusted source, inconsistent with the user's task | ASI01 | ATLAS AML.T0086 Exfiltration via AI Agent Tool Invocation | T3 |
| H05 | Mass read followed by export or send within one session by an agent whose role does not do that | ASI02 | ATLAS AML.T0086 | T2 |
| H06 | New secret or certificate added to an agent's service principal, or a sign-in from a first-seen IP | ASI03 | ATT&CK T1098.001, T1078.004 | T2 |
| H07 | Agent identity reads credentials unrelated to its task | ASI03, ASI05 | Runtime rule pattern for agent containers | T2 |
| H08 | Agent process spawns a shell or interpreter, or opens an outbound connection from a deny-by-default sandbox | ASI05 | Sandbox boundary violation | T2 |
| H09 | Agent MCP configuration or skill file modified outside change control | ASI04, ASI06 | Agent config tampering | T2 |
| H10 | Persistent memory write originating from an untrusted source | ASI06 | ATLAS AML.T0080 AI Agent Context Poisoning: Memory | T3 |
| H11 | Host with no approved AI use calls an LLM API, or a script calls one at runtime and executes the output | ASI05 | ATLAS AML.T0096 AI Service API; GTIG AI-enabled malware | T1 |
| H12 | Approval granted where the displayed action differs from the executed action | ASI09 | Human-agent trust exploitation | T3 |

**Where to start.** H06, H08, H09 and H11 need only T1 or T2 telemetry that many organizations already collect from identity, endpoint and proxy logs, so they can be validated first. H01 to H04 and H10 need T3 telemetry; treat them as the business case for the telemetry contract.

**Existing community work to reuse, not duplicate.** Open projects already publish rules and formats for this space, including [ATR (Agent Threat Rules)](https://github.com/dajiaohuang/agent-threat-rules), the [AI/ML DFIR detection pack](https://github.com/depalmar/ai-dfir-toolkit) and [sigma-ai-abuse-detections](https://github.com/Shubhmane9503/sigma-ai-abuse-detections). Their quality varies and each needs the same validation gates before you trust it. ASSAY's contribution is the method that connects such rules to telemetry, evidence and governance.

## Crosswalk to standards and frameworks (informative)

This table shows where ASSAY's layers touch widely used frameworks, so that a CISO can reuse evidence in an existing program. It is the author's interpretation. It does not confer compliance with any framework, and no framework body has reviewed it. Clause numbers come from search-result excerpts and should be checked against the published text before use.

| Framework | Reference | Where ASSAY connects |
| --- | --- | --- |
| NIST Cybersecurity Framework 2.0 | Functions Govern, Identify, Protect, Detect, Respond, Recover (function level only) | Detect: Layers 1 to 4. Govern: Layer 5, roles, autonomy tiers. Identify: the agent and MCP server inventory behind maturity level 1. Respond: the response block and T-Disrupt rules, which hand off to existing response plans |
| NIST AI Risk Management Framework 1.0 and the Generative AI Profile (AI 600-1) | Functions Govern, Map, Measure, Manage | Map: threat-to-detection mapping (Layer 2). Measure: validation gates and quality measures (Layer 4). Manage: governed deployment and rollback (Layer 5). Govern: roles and autonomy limits |
| ISO/IEC 27001:2022 | Annex A 8.15 (logging) and 8.16 (monitoring activities) | Layer 1 telemetry and log-health checks give evidence for logging; detections with gate evidence give evidence for monitoring |
| ISO/IEC 42001:2023 | Annex A control on recording of AI system event logs (A.6.2.8) | The Layer 1 agent event classes and identity lineage |
| EU AI Act (Regulation (EU) 2024/1689) | Article 12 (automatic logging), Article 19 (log keeping by providers) and Article 26(6) (log keeping by deployers, at least six months) | Layer 1 events can support such logging where a system is in scope. Whether a system is in scope, and from what date, depends on its classification and the Act's phased application dates, which this document does not state; take legal advice |
| OWASP Top 10 for Agentic Applications (ASI01 to ASI10) | Risk identifiers | The threat.owasp\_asi field in every DHR and the starter hypotheses H01 to H12 |
| MITRE ATLAS | Technique and case-study identifiers | The threat.atlas field, always with the release pinned |
| MITRE ATT&CK | Technique identifiers | The optional threat.attack field for conventional behavior inside an agent incident |
| OpenTelemetry GenAI conventions and OCSF | Telemetry schemas | The alignment column of the Layer 1 table |

## Limitations, open questions and contributing

This is version 0.1: a synthesis of public research and current practice, not a framework proven in production. Read the following as the honest boundary of what is claimed.

**Limitations.**

- **Thin evidence on agentic authoring.** The main quantitative study used here, AVDA, drew on one organization's detections and evaluated only OpenAI models; its authors also flag a small expert-validation sample. ASSAY's autonomy limits are conservative because the evidence is.
- **Unstable standards.** OpenTelemetry GenAI conventions are at Development stability, and the OCSF mapping for agents comes from community work rather than a settled standard. The Layer 1 field names will change.
- **Contested method.** Practitioners disagree on whether per-agent behavioral baselines are reliable. ASSAY supports both baselines and sandbox-boundary rules but does not settle the question.
- **Proposed, not measured, thresholds.** The impact tiers, autonomy levels, gate criteria and readiness levels are design proposals. No published data validates the specific cut-offs.
- **Source quality varies.** Several inputs are vendor blogs with commercial interests, and some incident detail is secondary reporting. Primary sources are linked where they exist.
- **Unvalidated catalog.** The twelve starter hypotheses have not been run against real telemetry, and their false-positive behavior is unknown.

**Open questions for the community.**

1. What should the canonical field names for agent identity lineage be, and should they live in OCSF, OpenTelemetry or both?
2. How should agent-authored precision be measured fairly against human-authored rules?
3. When is an LLM acceptable as a reviewer in the critique stage, given attacks aimed at LLM-based analysis?
4. How should multi-agent delegation chains be attributed when one agent invokes another on a user's behalf?
5. What is the lawful minimum of prompt and response capture for security purposes in regulated sectors?

## Governance, versioning and contribution

This section describes how the project is meant to be run once it has a public repository. Items marked proposed are intentions, not facts.

**Stewardship (proposed).** The author acts as sole maintainer until a maintainers group exists. Decisions are made in public issues with their rationale recorded. A maintainers group with members from at least two organizations is a condition for version 1.0.

**Repository files (proposed).** README, LICENSE, GOVERNANCE, CONTRIBUTING, CODE\_OF\_CONDUCT, SECURITY and CHANGELOG at the root, following common open-source project practice such as the OpenSSF best-practices criteria. SECURITY explains how to report privately a flaw in the schemas or guidance that could create a detection blind spot or an exploitable pipeline.

**Versioning.** The specification and each schema use semantic versioning. A MAJOR change removes or renames a requirement or required field, or otherwise makes a conformant claim non-conformant. A MINOR change adds optional fields, event classes or RECOMMENDED requirements. A PATCH change fixes wording or errors without changing meaning. Before 1.0, a MINOR change may break compatibility, and the changelog says so.

**Stable identifiers.** Requirement identifiers, DHR identifiers and event-class names are never reused. A deprecated item stays in the catalogue, marked, for at least one MINOR release before removal.

**Extensions.** Local fields use the x- prefix that both schemas reserve. An extension MUST NOT change the meaning of a defined field.

**Change process (proposed).** A material change starts as an issue-based proposal, stays open for public comment for at least 14 days, and is decided by the maintainers with the rationale recorded in the issue.

**Contributing.** Contributions are welcome as issues and pull requests: new or corrected hypotheses, validated fixtures, mappings to other schemas, field reports from real deployments, and evidence that changes a threshold. Proposed repository layout: spec/ for the text, schemas/ for the DHR and DLS schemas, catalog/ for hypothesis records, fixtures/ for labeled logs and scenarios, and templates/ for pipeline starters. Whether contributions need a sign-off or a contributor agreement is an open decision.

**License (proposed, to be confirmed by the author).** Specification text under Creative Commons Attribution 4.0; schemas, templates and code examples under Apache License 2.0.

**Name.** Conformance claims may use the name ASSAY only as the Conformance section words them. No trademark clearance has been performed.

## Path to v1.0

A specification without an implementation risks being agreed with and never used. This table lists what v1.0 needs and where this draft stands, in priority order.

| Priority | Item | State in this draft |
| --- | --- | --- |
| P0 | Detection Logic Specification | Elements, a draft JSON Schema and an example defined and checked against each other; no adapter or shared test scenarios yet |
| P0 | SIEM adapters | Adapter requirements defined; no adapters written |
| P0 | Formal Detection Hypothesis Record schema | Draft JSON Schema and example defined and checked against each other, with conditional rules; no independent implementation yet |
| P1 | Detection quality scoring | Measures and evidence statuses defined; scoring procedure and report format still needed |
| P1 | Agentic detection test library | Fixture approach described; no reusable scenarios published |
| P1 | Conformance | Normative clauses and evidence bundle defined in this draft; self-assessed only, with no test suite yet |
| P1 | Reference implementation | Deliberately out of scope for this spec-only draft; the first vertical slice below is its proposed start |

**First vertical slice.** Prove the method end to end on one scenario before widening it: an agent reads sensitive information and sends it to an unauthorized external destination.

1. Collect agent identity, user identity and credential information.
2. Collect tool-call events and destination information.
3. Write the hypothesis record for suspicious read-then-export behavior.
4. Write the detection logic specification.
5. Generate a real SIEM query through an adapter.
6. Replay benign and malicious scenarios, including variants.
7. Measure detection quality and false positives.
8. Promote the detection through the approval workflow for its tier.

Then repeat the process for three more scenarios: unauthorized MCP server registration, agent credential misuse, and an agent spawning shell commands or running unexpected code. Four scenarios demonstrated end to end would give the community something concrete to test and challenge.

## Sources

Researched 11 and 12 November 2026. A few pages were opened in full (AVDA, the SANS and Anvilogic summary, the Cycode OWASP walkthrough and the Nebulock project pages); the others, including every standard and prior-art item added in the second pass, were read as search-result excerpts, so check the original before quoting a figure or a clause number. The references are split into normative (needed to apply the specification) and informative.

**Detection engineering practice**

- [SANS and Anvilogic, State of Detection Engineering 2026](https://www.anvilogic.com/report/state-of-detection-engineering)
- [CardinalOps SIEM detection risk report, via Dark Reading](https://www.darkreading.com/analytics/enterprise-siem-blind-mitre-attack-coverage)
- [AVDA: Autonomous Vibe Detection Authoring for Cybersecurity (arXiv 2603.25930)](https://arxiv.org/pdf/2603.25930)
- [Microsoft, The agentic SOC](https://www.microsoft.com/en-us/security/blog/2026/04/09/the-agentic-soc-rethinking-secops-for-the-next-decade/)
- [NHI Mgmt Group, governing agents that write detections](https://nhimg.org/faq/how-should-security-teams-govern-ai-agents-that-write-detections-and-hunt-across/)
- [BlueTeamCon 2026, detection regression testing](https://blueteamcon2026.sched.com/event/2P73O)
- [Sigma Specification 2.0 overview (Graylog)](https://graylog.org/post/sigma-specification-2-0-what-you-need-to-know)

**Threats and taxonomies**

- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/2025-12-09/owasp-top-10-for-agentic-applications-for-2026) and [Cycode walkthrough](https://cycode.com/blog/owasp-top-10-agentic-applications/)
- [MITRE ATLAS v2026.09 (Speakeasy)](https://www.speakeasy.com/blog/mitre-atlas-explained)
- [ATLAS case study AML.CS0053, postmark-mcp](https://www.startupdefense.io/mitre-atlas-case-studies/aml-cs0053-poisoned-postmark-mcp-server-email-exfiltration)
- [postmark-mcp incident (MintMCP)](https://www.mintmcp.com/blog/postmark-mcp-malicious-server-email-exfiltration)
- [MCP trust-boundary research (Security Boulevard)](https://securityboulevard.com/2026/04/attacking-the-mcp-trust-boundary/)
- [Anthropic, Disrupting the first reported AI-orchestrated cyber espionage campaign](https://www.anthropic.com/news/disrupting-AI-espionage)
- [Google GTIG AI Threat Tracker](https://cloud.google.com/blog/topics/threat-intelligence/threat-actor-usage-of-ai-tools)

**Telemetry, identity and runtime detection**

- [OpenTelemetry GenAI conventions explained (Dash0)](https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained)
- [AOS tracing with OCSF](https://aos.owasp.org/spec/trace/extend_ocsf/)
- [Detecting AI agents and non-human identities in Microsoft Sentinel](https://techcommunity.microsoft.com/t5/microsoft-sentinel/detecting-ai-agents-and-non-human-identities-in-microsoft/m-p/4526787)
- [ARMO, detecting prompt injection in production agent workloads](https://www.armosec.io/blog/how-to-detect-prompt-injection-in-production-ai-agent-workloads/)
- [Sysdig, runtime security for agentic AI tooling](https://www.sysdig.com/blog/agentic-ai-tooling-why-runtime-security-is-the-missing-layer)
- [Indirect prompt injection in tool-calling agents: detection shape (trackr)](https://www.trackr.live/?p=1076)

**Open-source prior art**

- [ATR, Agent Threat Rules](https://github.com/dajiaohuang/agent-threat-rules)
- [AI/ML DFIR detection pack](https://github.com/depalmar/ai-dfir-toolkit)
- [sigma-ai-abuse-detections](https://github.com/Shubhmane9503/sigma-ai-abuse-detections)
- [RSigma](https://github.com/timescale/rsigma)
- [Nebulock Agentic Detection Engineering Framework](https://github.com/Nebulock-Inc/agentic-detection-engineering-framework)
- [AI Detection Engineering maturity matrix (infosecb)](https://infosecb.github.io/detection-engineering-ai-maturity/matrix/)

**Open-source and community prior art, continued**

- [Vega Detection Skills announcement](https://vega.io/blog/vega-introduces-detection-skills)
- [OpenTIDE (OpenTideHQ)](https://github.com/OpenTideHQ)
- [Detecting Offensive Cyber Agents: A Detection-in-Depth Approach (IAPS, includes the Agentic Security Alert Standard)](https://arxiv.org/pdf/2605.21956)
- [AARTS, AI Agent Runtime Safety Standard (Gen Digital)](https://www.gendigital.com/blog/news/company-news/ai-agent-runtime-security)

**Normative references**

- [RFC 2119, Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/info/rfc2119)
- [RFC 8174, Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://www.rfc-editor.org/info/rfc8174)
- [JSON Schema, draft 2020-12](https://json-schema.org/draft/2020-12)

**Informative references (crosswalk)**

- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [ISO/IEC 27001:2022](https://www.iso.org/standard/27001)
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)
- [Regulation (EU) 2024/1689, the AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [OpenSSF Best Practices criteria](https://www.bestpractices.dev/)
