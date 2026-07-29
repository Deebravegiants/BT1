import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the path from https:///github.com/dfinity/ICRC-1
SOURCE_REPO = "near/core-contracts"
# todo: the name of the repository
REPO_NAME = "core-contracts"
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

scope_files = [
    "lockup/src/foundation.rs",
    "lockup/src/foundation_callbacks.rs",
    "lockup/src/gas.rs",
    "lockup/src/getters.rs",
    "lockup/src/internal.rs",
    "lockup/src/lib.rs",
    "lockup/src/owner.rs",
    "lockup/src/owner_callbacks.rs",
    "lockup/src/types.rs",
    "staking-pool/src/internal.rs",
    "staking-pool/src/lib.rs",
    "staking-pool-factory/src/lib.rs",
    "staking-pool-factory/src/utils.rs",
    "whitelist/src/lib.rs",
    "multisig/src/lib.rs",
]

target_scopes = [
    "Critical. Unauthorized transfer, withdrawal, spending, or release of locked, vested, pooled, or multisig-controlled NEAR through public-call, callback, approval, or accounting failure reachable by an unprivileged user",
    "Critical. Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release, vesting termination, unstake-withdraw, factory refund, or multisig request execution flows",
    "High. Unauthorized execution, confirmation bypass, or state-transition bypass in multisig, lockup, staking-pool, staking-pool-factory, or whitelist flows that lets an unprivileged user perform actions beyond intended authority",
    "High. Share, reward, vesting, refund, whitelist, or balance-accounting divergence that lets an unprivileged user over-credit value, bypass fees or limits, or withdraw more than fair entitlement",
    "High. Replay, duplicate-effect, callback-ordering, cooldown, nonce, or account-binding failure in request, pool-creation, transfer-availability, staking, or withdrawal flows that breaks single-execution or rightful redemption guarantees",
    "Critical. Unauthorized extraction of funds from lockup custody, including vested or released balances, by abusing public owner-path assumptions, callback state, or staking-pool integration without privileged access",
    "Critical. Permanent inability for a legitimate user to recover locked, unstaked, refunded, or multisig-scheduled funds because of reachable state-machine deadlock, callback desynchronization, or irreversible accounting corruption",
    "High. Multisig request lifecycle flaws that let an unprivileged attacker cause unintended execution, deletion, confirmation side effects, request corruption, or durable denial of rightful request completion",
    "High. Staking share-price, reward distribution, rounding, or unstake-window edge cases that let an unprivileged user obtain excess stake value, withdraw against incomplete backing, or strand other users' balances",
    "High. Factory, whitelist, account-id, or callback-binding flaws that let an unprivileged user create, whitelist, refund, or bind staking-pool state in a way that violates intended custody, authorization, or redemption guarantees",
]



def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit + fuzzing questions for one core-contracts production target.

    ```
    target_file format:
    "'File Name: lockup/src/lib.rs -> Scope: Critical. Unauthorized transfer, withdrawal, spending, or release of locked, vested, pooled, or multisig-controlled NEAR through public-call, callback, approval, or accounting failure reachable by an unprivileged user'"
    ```
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit and fuzzing questions for this exact NEAR core-contracts target:

    {target_file}

    Use live context from the project if available: lockup owner/foundation methods, vesting and release math, transfer-enable checks, staking-pool selection and callbacks, staking-pool deposit/stake/unstake/withdraw/share-price logic, staking-pool-factory create/whitelist/refund callbacks, whitelist foundation/factory authorization, and multisig request/confirm/delete/execute/key-management flows.

    Protocol focus:
    This repository implements core NEAR custody and control contracts: token lockups with vesting and staking integrations, staking pools and factory deployment, whitelist-based pool admission, and multisig request execution. The audit focus is whether a strictly unprivileged external user can reach unauthorized fund movement, unauthorized action execution, excess value extraction, or permanent fund lock through public methods, callback sequencing, accounting edge cases, request lifecycle bugs, or account-binding mistakes.

    Core invariants:

    * Locked, vested, staked, unstaked, refunded, or multisig-controlled balances must never become withdrawable or spendable by the wrong account.
    * Every sensitive state transition must stay bound to the intended predecessor, signer key, owner/foundation role, request, pool, and callback result.
    * Share, reward, vesting, release, refund, and withdrawal accounting must remain monotonic and must not over-credit an attacker.
    * Request execution, unstake/withdraw windows, pool creation, and callback chains must not be replayable, duplicated, or left in a fund-locking bad state.

    Rules:

    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Attacker is strictly unprivileged: a normal external account or contract caller with no owner, foundation, factory, whitelist, multisig signer, validator, or protocol-level privileges.
    * Do not rely on malicious owners, foundation, validators, multisig key holders, privileged accounts, leaked keys, governance abuse, malicious peers or nodes, social engineering, front-run-only paths, network-level DoS, chain-level attacks, or public-mainnet testing.
    * Do not generate questions that depend only on gas griefing, storage bloat, harmless reverts, logging noise, best-practice commentary, or self-loss without protocol break.
    * Do not generate self-harm or user-mistake-only scenarios.
    * Generate 20 to 30 high-signal questions.
    * At least 70% must be multi-step flow, invariant, fuzz, accounting, callback, replay, or cross-module questions.
    * Every question must be testable by PoC, unit test, fuzz test, invariant test, or differential test.
    * Avoid generic checklist questions and repeated root causes.
    * Every question must target a plausible valid issue.

    Investigation process:

    * Anchor on the exact target file/module, its public entrypoints, trust boundaries, and downstream state changes.
    * Generate questions from five distinct lenses so the audit path differs from a generic sweep:
      - authorization/binding failures;
      - accounting/share/vesting failures;
      - state-machine/callback failures;
      - replay/duplicate-effect failures;
      - parsing/account-id/input-shaping failures.
    * Prefer questions that need at least two steps, two modules, or one valid-looking check that binds the wrong thing.
    * Remove paraphrases and keep only distinct root causes.
    * Bias toward counterexamples where an unprivileged attacker passes visible checks but still reaches an invalid state transition.

    High-value attack surfaces:

    * Lockup flows: release/vesting math, transfer availability, staking pool selection, owner withdrawals, foundation termination, and termination callbacks.
    * Staking pool flows: deposit, deposit_and_stake, unstake, withdraw, ping reward distribution, share conversions, and pause/restake behavior.
    * Factory and whitelist flows: pool account creation, whitelist callback success/failure, refund path, factory delegation, and account-id validation/binding.
    * Multisig flows: add_request, confirm, delete_request, execute_request, key changes, request limits, cooldown, and self-call assumptions.
    * Cross-module state: predecessor/signer binding, promise-result handling, callback ordering, and one-time execution assumptions.

    Impact mapping:

    * Critical: Unauthorized transfer, withdrawal, spending, or release of locked, vested, pooled, or multisig-controlled NEAR through public-call, callback, approval, or accounting failure reachable by an unprivileged user.
    * Critical: Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release, vesting termination, unstake-withdraw, factory refund, or multisig request execution flows.
    * High: Unauthorized execution, confirmation bypass, or state-transition bypass in multisig, lockup, staking-pool, staking-pool-factory, or whitelist flows that lets an unprivileged user perform actions beyond intended authority.
    * High: Share, reward, vesting, refund, whitelist, or balance-accounting divergence that lets an unprivileged user over-credit value, bypass fees or limits, or withdraw more than fair entitlement.
    * High: Replay, duplicate-effect, callback-ordering, cooldown, nonce, or account-binding failure in request, pool-creation, transfer-availability, staking, or withdrawal flows that breaks single-execution or rightful redemption guarantees.

    Coverage requirements:

    * At least half of the questions must explicitly mention one of: signer/predecessor binding, callback ordering, share or reward math, vesting/release state, request lifecycle, refund path, or account-id validation.
    * Prefer invariant tests, stateful fuzzing, and multi-call PoCs over one-call revert checks.

    Each question must include:

    1. target function/module;
    2. attacker action;
    3. preconditions;
    4. call sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_module] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: fuzz/state-test PARAMETERS and assert EXPECTED_PROPERTY.",
    ]
    """
    return prompt


def audit_format(question: str) -> str:
    """
    Generate a focused core-contracts exploit-question validation prompt.
    """
    return f"""# QUESTION SCAN PROMPT

## Exploit Question
{question}

Focus only on production NEAR core-contracts code in `scope_files`, mainly:
- lockup/src
- staking-pool/src
- staking-pool-factory/src
- whitelist/src
- multisig/src
Anything outside those production files is out of scope unless needed as direct supporting context.

## Rules
- Audit only production NEAR core-contracts code.
- Treat repo context as accessible. Do not ask for files or claim they are missing.
- Ignore tests, docs, mocks, e2e assets, scripts, configs, build files, IDE files, package metadata, vendored libraries, and local-only fixtures.
- The attacker must be strictly unprivileged and must enter through public contract methods, public callbacks reachable from those methods, attached deposits, account IDs, request submission, or other normal external inputs.
- Reject self-harm or user-mistake-only paths: wrong recipient chosen by the sender, voluntary self-loss, or cases where the attacker can only damage their own funds without violating protocol guarantees.
- Prefer #NoVulnerability unless the path is concrete, locally testable, and bounty-grade.

## Allowed Impact Scope
Only these impacts are valid:
- Critical. Unauthorized transfer, withdrawal, spending, or release of locked, vested, pooled, or multisig-controlled NEAR through public-call, callback, approval, or accounting failure reachable by an unprivileged user.
- Critical. Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release, vesting termination, unstake-withdraw, factory refund, or multisig request execution flows.
- High. Unauthorized execution, confirmation bypass, or state-transition bypass in multisig, lockup, staking-pool, staking-pool-factory, or whitelist flows that lets an unprivileged user perform actions beyond intended authority.
- High. Share, reward, vesting, refund, whitelist, or balance-accounting divergence that lets an unprivileged user over-credit value, bypass fees or limits, or withdraw more than fair entitlement.
- High. Replay, duplicate-effect, callback-ordering, cooldown, nonce, or account-binding failure in request, pool-creation, transfer-availability, staking, or withdrawal flows that breaks single-execution or rightful redemption guarantees.

## Method
1. Trace the attacker-controlled entrypoint and exact production functions touched.
2. Check the binding or invariant being challenged: authorization, signer/predecessor binding, accounting, callback order, request lifecycle, or input validation.
3. Decide whether the exploit still works under current checks.
4. Prove root cause with exact file/function/line references.
5. Confirm exact scoped impact and realistic likelihood.

## Reject Immediately
- Requires a trusted role, privileged account, foundation/owner/factory authority, multisig signer privilege, validator control, leaked key, or external dependency compromise.
- Requires phishing, malicious peers or nodes, chain attacks, network-level DoS only, or public-mainnet testing.
- Only affects tests, docs, configs, scripts, mocks, fixtures, vendored code, or local deployment choices.
- Is self-harm-only, local misconfiguration, logging/observability noise, harmless revert, stale read, gas griefing, or theory without a concrete exploit path.

## Output
If valid:

### Title
[Clear vulnerability statement] - ([File: file_path])

### Summary
### Finding Description
### Impact Explanation
### Likelihood Explanation
### Recommendation
### Proof of Concept

If invalid, output exactly:
#NoVulnerability found for this question.
"""


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for core-contracts.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

Focus only on production NEAR core-contracts code in `scope_files`, mainly:
- lockup/src
- staking-pool/src
- staking-pool-factory/src
- whitelist/src
- multisig/src
Anything outside those production files is out of scope unless needed as direct supporting context.

## Rules
- Treat production NEAR core-contracts files as accessible context. Do not claim files are missing or inaccessible.
- Do not ask for repository contents.
- Do not scan tests, docs, build files, IDE files, configs, resources, local fixtures, vendored libraries, package metadata, or e2e assets as audited targets.
- Use the external report only as a hint. Report an analog only if core-contracts has its own reachable root cause.
- The attacker must be strictly unprivileged and must enter through public protocol inputs.
- Reject self-harm or user-mistake-only paths.

## Allowed Impact Scope
Only these impacts are valid:
- Critical. Unauthorized transfer, withdrawal, spending, or release of locked, vested, pooled, or multisig-controlled NEAR through public-call, callback, approval, or accounting failure reachable by an unprivileged user.
- Critical. Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release, vesting termination, unstake-withdraw, factory refund, or multisig request execution flows.
- High. Unauthorized execution, confirmation bypass, or state-transition bypass in multisig, lockup, staking-pool, staking-pool-factory, or whitelist flows that lets an unprivileged user perform actions beyond intended authority.
- High. Share, reward, vesting, refund, whitelist, or balance-accounting divergence that lets an unprivileged user over-credit value, bypass fees or limits, or withdraw more than fair entitlement.
- High. Replay, duplicate-effect, callback-ordering, cooldown, nonce, or account-binding failure in request, pool-creation, transfer-availability, staking, or withdrawal flows that breaks single-execution or rightful redemption guarantees.

## Method
1. Classify the external bug class: authorization, accounting, state machine, replay, or input binding.
2. Map that class to exact core-contracts production files and attacker-controlled entrypoints.
3. Prove core-contracts has its own root cause with exact file/function/line references.
4. Confirm exact scoped impact and realistic likelihood.

## Disqualify Immediately
- No reachable attacker-controlled entry path.
- Requires trusted role, privileged account, owner/foundation/factory authority, multisig signer privilege, validator control, leaked key, or external dependency compromise.
- Requires phishing, public-mainnet testing, malicious peer/node assumptions, chain attack assumptions, or network-level DoS only.
- Is test/docs/config/build-only, self-harm-only, theoretical-only, or has no matching in-scope impact.
- Impact is only local misconfiguration, observability/logging noise, harmless revert, stale read, gas griefing, or non-security correctness.

## Output (Strict)
If valid analog exists, output:

### Title
[Clear vulnerability statement] - ([File: file_path])

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
    Generate a strict core-contracts bounty-style validation prompt for security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

Focus only on production NEAR core-contracts code in `scope_files`, mainly:
- lockup/src
- staking-pool/src
- staking-pool-factory/src
- whitelist/src
- multisig/src
Anything outside those production files is out of scope unless needed as direct supporting context.

## Rules
- Validate only the submitted claim.
- Check SECURITY.md, Researcher.md if present, and the bounty scope for exclusions and valid impact classes.
- Do not create a new issue if the claim is weak.
- Do not upgrade severity unless the evidence proves it.
- The exploit must be triggerable by a strictly unprivileged user through public lockup, staking, factory, whitelist, or multisig-call flows, unless the claim proves privilege escalation from such a path.
- Reject self-harm or user-mistake-only scenarios.
- Reject malicious-owner-only, malicious-foundation-only, privileged-only, leaked-key, malicious-validator-only, malicious-peer/node-only, host-compromise, best-practice, docs/style, config/test-only, gas-only, front-run-only, network-level-DoS-only, and purely theoretical claims.
- Reject assumptions that require phishing, governance/51% control, third-party compromise, unsupported protocol behavior, or NEAR base-chain attacks.
- Prefer #NoVulnerability over speculation.

## In-Scope Areas
- Lockup flows: initialization, release/vesting math, transfer-enable gating, staking-pool selection, owner withdrawals, foundation termination, and callbacks.
- Staking pool flows: deposit, deposit_and_stake, unstake, withdraw, ping reward distribution, share math, pause/resume, and owner-controlled validator settings.
- Factory and whitelist flows: pool creation, account-id derivation, callback refund handling, whitelist admission, and factory delegation checks.
- Multisig flows: request creation, confirmation, deletion cooldown, execution, key management, and self-call assumptions.
- Shared production helpers and types used directly by those in-scope contracts.
- Reject other contracts in this repo, tests, docs, examples, mocks, generated files, local deployment helpers, vendored libraries, e2e tooling, and local developer tooling unless the claim proves direct impact on the in-scope contracts above.

## Allowed Impact Scope
Only these impacts are valid:
- Critical. Unauthorized transfer, withdrawal, spending, or release of locked, vested, pooled, or multisig-controlled NEAR through public-call, callback, approval, or accounting failure reachable by an unprivileged user.
- Critical. Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in lockup release, vesting termination, unstake-withdraw, factory refund, or multisig request execution flows.
- High. Unauthorized execution, confirmation bypass, or state-transition bypass in multisig, lockup, staking-pool, staking-pool-factory, or whitelist flows that lets an unprivileged user perform actions beyond intended authority.
- High. Share, reward, vesting, refund, whitelist, or balance-accounting divergence that lets an unprivileged user over-credit value, bypass fees or limits, or withdraw more than fair entitlement.
- High. Replay, duplicate-effect, callback-ordering, cooldown, nonce, or account-binding failure in request, pool-creation, transfer-availability, staking, or withdrawal flows that breaks single-execution or rightful redemption guarantees.

Anything limited to observability, non-security correctness, harmless revert/reject, stale read, local misconfiguration, self-loss without protocol break, or non-demonstrable exploitation is invalid.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken security/accounting/binding assumption.
3. Reachable exploit path: preconditions -> attacker action -> trigger -> bad result.
4. Existing checks reviewed and shown insufficient.
5. Concrete allowed impact with realistic likelihood.
6. Reproducible proof path: PoC, integration test, invariant/fuzz test, differential test, or exact local steps.
7. No obvious exclusion, privilege requirement, or self-harm-only framing.

## Silent Triage Questions
Before output, internally answer:
- Can a normal unprivileged external user trigger this through a public core-contracts path?
- Does the code actually behave as claimed?
- Is the impact caused by core-contracts production code, not an external dependency alone?
- Is the impact concrete, in-scope, and not just self-loss or theory?
- Would a bounty triager accept the proof, and what exact test proves it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the bug and impact]

## Finding Description
[Exact code path, root cause, exploit flow, and why existing checks fail]

## Impact Explanation
[Concrete allowed core-contracts bounty impact and severity rationale]

## Likelihood Explanation
[Attacker capability, required conditions, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or fuzz/invariant/fork test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt
