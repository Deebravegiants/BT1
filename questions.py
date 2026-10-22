import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 25
# todo: the path from https://github.com/rsksmart/rsk-powhsm
SOURCE_REPO = "AuditingProject/AllProjects"
# todo: the name of the repository
REPO_NAME = "AllProjects"
run_number = os.environ.get('GITHUB_RUN_NUMBER') or os.environ.get('CI_PIPELINE_IID', '0')


def get_cyclic_index(run_number, max_index=100):
    """Convert run number to a cyclic index between 1 and max_index"""
    return (int(run_number) - 1) % max_index + 1


def load_repository_urls():
    """Load repository URLs from repositories.json."""
    repo_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repositories.json")
    if not os.path.exists(repo_file):
        return []

    try:
        with open(repo_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return [url for url in data if isinstance(url, str) and url.strip()]


if run_number == "0":
    BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"
else:
    repository_urls = load_repository_urls()
    if repository_urls:
        run_index = get_cyclic_index(run_number, len(repository_urls))
        BASE_URL = repository_urls[run_index - 1]
    else:
        BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one AllProjects target.

    ```
    target_file format:
    "'File Name: project_name/path/to/file -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit questions for this exact target in the AllProjects repository:

    {target_file}

    Project focus:
    AllProjects is a collection of independent projects, each in its own top-level folder. The first path segment of `File Name:` is the project. Use that project's README, SECURITY.md, docs and audit/bounty scope to understand what it protects (funds, keys, accounting, authorization, protocol state) and how untrusted input reaches the target file.

    Rules:
    * Treat `File Name:` as the exact file and `Scope:` as the ONLY impact to target.
    * Assume full repo context. Do not ask for code or say anything is missing.
    * Use exact symbols (function, method, struct, field, constant, error) when possible.
    * Attacker is unprivileged only: an ordinary user, caller, contract deployer, transaction sender or network participant using the project's public entry points.
    * Attacker is NOT an admin, owner, governance role, trusted operator, oracle, relayer, validator majority or malicious peer/node, holds no leaked keys or credentials, and has no physical or local access. Never assume social engineering.
    * Out of scope, never ask about: anything the project's own scope docs exclude, third-party/vendored dependencies, tests, mocks, scripts, examples, deployment and tooling.
    * Ignore test files, mocks, fuzz harnesses, build and generated code.
    * Every question must be a real scenario an unprivileged attacker can cause in production: concrete inputs, the exact call or transaction sequence, and the state the system is in. No unbounded-loop, memory-exhaustion, gas-griefing, CPU or "huge input" questions.
    * Generate 40 to 80 high-signal questions, at least 70% aimed at Critical impact. No generic checklist items or repeated root causes.
    * Every question must be testable with the project's own unit/integration tests, a local fork or harness, or a fuzz/property test.

    Core invariants:
    * Authorization: only the rightful party can move funds, sign, or change protected state.
    * Accounting: balances, shares, supply and debts stay consistent; no value is created or lost.
    * Validation: proofs, signatures, messages and inputs are fully checked before use; a failed or partial operation never leaves usable state.
    * Binding: one authorization or proof is used exactly once, for exactly the action it was checked against; no replay across contexts, chains or resets.
    * Secrets: no private key, seed or secret leaves its boundary.

    Each question must include:
    1. target function;
    2. attacker action (inputs or transactions the attacker creates);
    3. preconditions (system state, configuration, balances);
    4. call sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS cause CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: test PARAMETERS and assert AUTHORIZATION, ACCOUNTING, VALIDATION, BINDING, or SECRETS.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused AllProjects exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- The repository is AllProjects: independent projects, each in its own top-level folder. Use existing repo context only. Analyze only this question, its project and scoped impact.
- Respect the project's own scope: README, SECURITY.md, audit scope or bounty docs.
- Attacker is unprivileged only: an ordinary user, caller, contract deployer, transaction sender or network participant using public entry points.
- Reject admin/owner/governance roles, trusted operators, oracles or relayers, malicious peers/nodes, leaked keys or credentials, physical or local access and social engineering.
- Reject out-of-scope components, third-party/vendored code, tests/mocks/fuzz code, scripts, deployment and tooling.
- Reject unbounded-loop, memory-exhaustion, gas-griefing, CPU and local-access DoS claims.
- Focus on real impact: theft or loss of funds, permanent freezing of funds, protocol insolvency, unauthorized signing or authenticated actions, key or secret extraction.

## Validate
- Trace the exact path from the attacker's input or transaction through the entry point to the check that fails.
- Check existing guards: access control, input and bounds validation, signature/proof verification, state transitions, accounting updates, replay protection, arithmetic safety.
- Confirm the path is reachable in the production build or deployment, not only in tests or debug configurations.
- Accept only concrete fund loss, frozen funds, insolvency, unauthorized actions or secret exposure.
- Require exact project/file/function support and a reproducible PoC (test, fork or harness run).

## Output
If valid, output exactly:

### Title
[Bug statement] - ([Project: project_name] [File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker input, call sequence, and why existing checks fail]

### Impact Explanation
[Concrete impact and severity, per the project's bounty or severity guidelines]

### Likelihood Explanation
[Preconditions, attacker cost, system state, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Test plan or harness input with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for the AllProjects repository.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- The repository is AllProjects: a collection of independent projects, each in its own top-level folder. Use existing repo context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint. Search every project for the same class; each analog must stand on that project's own code.
- For each project, respect its own scope: README, SECURITY.md, audit scope or bounty docs. Use in-scope production code only; ignore tests, mocks, scripts, examples, deployment, generated and vendored/third-party code.
- Keep only analogs an unprivileged party can reach: an ordinary user, caller, contract deployer, transaction sender or network participant using public entry points. No admin/owner/governance roles, trusted operators or oracles, malicious peers/nodes, leaked keys, physical or local access, or social engineering.
- Map the class onto each project's real shape: entry points and input parsing, authorization and access checks, proof/signature verification, state transitions and accounting, cross-component or cross-chain message handling, replay and binding, arithmetic and bounds, key and secret handling.
- Reject privileged, trusted-role, leaked-key, tests/mocks, out-of-scope, unbounded-loop/memory/gas-griefing/DoS, and no-impact analogs.
- Critical, High and Medium only, with concrete impact.

## Validate
- Map the class to the strongest path an unprivileged attacker can trigger in a specific project, naming the exact entry point, inputs and call sequence.
- Check existing guards and show why they fail.
- Prove root cause with exact project/file/function support.
- Accept only theft or loss of funds, permanent freezing of funds, protocol insolvency, unauthorized signing or authenticated actions, key or secret extraction, or a concrete break of a core protocol invariant.

## Output (Strict)
If valid analog exists, output:

### Title
[Clear vulnerability statement] - ([Project: project_name] [File: file_path])

### Summary
### Finding Description
### Impact Explanation
### Likelihood Explanation
### Recommendation
### Proof of Concept

If not, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for AllProjects security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- The repository is AllProjects: independent projects, each in its own top-level folder. Identify the claim's project and check its README, SECURITY.md, audit and bounty docs for scope, exclusions and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the evidence proves the higher impact.
- Accepted impacts: Critical (direct theft of user or protocol funds; permanent freezing of funds; protocol insolvency; key or secret extraction; unauthorized authenticated actions on behalf of others). High and Medium only if the project's severity guidelines list them and the impact is concrete. Reject Low, informational and best-practice findings.
- Reject out-of-scope components, third-party/vendored code, tests/mocks/fuzz, scripts, deployment and tooling, and DoS in general.
- Reject anything needing leaked keys or credentials, phishing or social engineering, admin/owner/governance roles, trusted operators, oracles or relayers, malicious peers/nodes, or physical or local access.
- Reject if the exploit needs more than an unprivileged user, caller, contract deployer, transaction sender or network participant.
- Reject if already fixed, acknowledged, in a known audit report, or public. A runnable PoC is mandatory; prefer #NoVulnerability over speculation.

## Required Validation Checks
All must pass:
1. Exact in-scope project, file, function, and line/code references in production code.
2. Clear root cause and a broken invariant (authorization, accounting, validation, binding, secrets) from the project's docs or code.
3. Reachable path: attacker input or transaction -> entry point -> system state -> bad result.
4. Existing guards reviewed and shown insufficient: access control, input and bounds checks, signature/proof verification, state transitions, accounting, replay protection, arithmetic safety.
5. Concrete accepted impact with realistic likelihood.
6. Reproducible PoC (test, fork, harness run, or crafted call sequence).
7. No rejection reason from the project's scope docs, exclusions, or privilege assumptions.

## Silent Triage Questions
Before output, internally answer:
- Can an unprivileged attacker trigger this with no special role, key or trusted position?
- Does it work in the production build or deployment, not just tests?
- Is the impact caused by the project's own in-scope code, not a dependency or external system?
- Does it cause concrete fund loss, frozen funds, insolvency, unauthorized actions or secret exposure?
- What exact test proves it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([Project: project_name] [File: file_path])

## Summary
[2-3 sentence summary of the bug and impact]

## Finding Description
[Exact code path, root cause, exploit flow, and why existing guards fail]

## Impact Explanation
[Concrete impact, severity, and impact category]

## Likelihood Explanation
[Attacker capability, cost and state required, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt
