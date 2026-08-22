import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = 'near/nearcore'
# todo: the name of the repository
REPO_NAME = 'nearcore'

run_number = os.environ.get('GITHUB_RUN_NUMBER', '0')


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
    # =================================================================================
    # Runtime: transaction/receipt validation, action execution, balance & gas accounting
    # =================================================================================
    "runtime/runtime/src/lib.rs",
    "runtime/runtime/src/verifier.rs",
    "runtime/runtime/src/actions.rs",
    "runtime/runtime/src/action_validation.rs",
    "runtime/runtime/src/access_keys.rs",
    "runtime/runtime/src/adapter.rs",
    "runtime/runtime/src/config.rs",
    "runtime/runtime/src/congestion_control.rs",
    "runtime/runtime/src/contract_code.rs",
    "runtime/runtime/src/conversions.rs",
    "runtime/runtime/src/deterministic_account_id.rs",
    "runtime/runtime/src/ext.rs",
    "runtime/runtime/src/function_call.rs",
    "runtime/runtime/src/global_contracts.rs",
    "runtime/runtime/src/pipelining.rs",
    "runtime/runtime/src/prefetch.rs",
    "runtime/runtime/src/receipt_manager.rs",
    "runtime/runtime/src/state_viewer/mod.rs",
    "runtime/runtime/src/types.rs",
    "runtime/runtime/src/bandwidth_scheduler/mod.rs",
    "runtime/runtime/src/bandwidth_scheduler/scheduler.rs",
    "runtime/runtime/src/bandwidth_scheduler/distribute_remaining.rs",

    # =================================================================================
    # VM runner: wasm preparation, instrumentation, imports, host logic, gas metering
    # =================================================================================
    "runtime/near-vm-runner/src/runner.rs",
    "runtime/near-vm-runner/src/prepare.rs",
    "runtime/near-vm-runner/src/prepare/prepare_v2.rs",
    "runtime/near-vm-runner/src/prepare/prepare_v3.rs",
    "runtime/near-vm-runner/src/prepare/instrument_v3.rs",
    "runtime/near-vm-runner/src/imports.rs",
    "runtime/near-vm-runner/src/cache.rs",
    "runtime/near-vm-runner/src/features.rs",
    "runtime/near-vm-runner/src/errors.rs",
    "runtime/near-vm-runner/src/profile.rs",
    "runtime/near-vm-runner/src/utils.rs",
    "runtime/near-vm-runner/src/logic/logic.rs",
    "runtime/near-vm-runner/src/logic/gas_counter.rs",
    "runtime/near-vm-runner/src/logic/vmstate.rs",
    "runtime/near-vm-runner/src/logic/context.rs",
    "runtime/near-vm-runner/src/logic/dependencies.rs",
    "runtime/near-vm-runner/src/logic/errors.rs",
    "runtime/near-vm-runner/src/logic/types.rs",
    "runtime/near-vm-runner/src/logic/utils.rs",
    "runtime/near-vm-runner/src/logic/alt_bn128.rs",
    "runtime/near-vm-runner/src/logic/bls12381.rs",
    "runtime/near-vm-runner/src/logic/recorded_storage_counter.rs",
    "runtime/near-vm-runner/src/wasmtime_runner/mod.rs",
    "runtime/near-vm-runner/src/wasmtime_runner/logic.rs",
    "runtime/near-vm-runner/src/wasmtime_runner/trap_classification.rs",

    # =================================================================================
    # Protocol primitives: transactions, actions, receipts, accounts, ids, serialization
    # =================================================================================
    "core/primitives/src/transaction.rs",
    "core/primitives/src/receipt.rs",
    "core/primitives/src/action/mod.rs",
    "core/primitives/src/action/delegate.rs",
    "core/primitives/src/signable_message.rs",
    "core/primitives/src/errors.rs",
    "core/primitives/src/trie_key.rs",
    "core/primitives/src/utils.rs",
    "core/primitives/src/congestion_info.rs",
    "core/primitives/src/bandwidth_scheduler.rs",
    "core/primitives/src/state_record.rs",
    "core/primitives/src/universal_state_init.rs",
    "core/primitives/src/views.rs",
    "core/primitives/src/utils/compression.rs",
    "core/primitives-core/src/account.rs",
    "core/primitives-core/src/code.rs",
    "core/primitives-core/src/config.rs",
    "core/primitives-core/src/gas.rs",
    "core/primitives-core/src/global_contract.rs",
    "core/primitives-core/src/deterministic_account_id.rs",
    "core/primitives-core/src/universal_account_id.rs",
    "core/primitives-core/src/universal_state_init.rs",
    "core/primitives-core/src/trie_key.rs",
    "core/primitives-core/src/serialize.rs",
    "core/primitives-core/src/hash.rs",
    "core/primitives-core/src/types.rs",
    "core/primitives-core/src/errors.rs",

    # =================================================================================
    # Protocol fee/limit configuration consumed by validation and metering
    # =================================================================================
    "core/parameters/src/config.rs",
    "core/parameters/src/cost.rs",
    "core/parameters/src/vm.rs",
    "core/parameters/src/parameter_table.rs",

    # =================================================================================
    # Storage: trie reads/writes, storage accounting, witness recording, flat storage
    # =================================================================================
    "core/store/src/trie/mod.rs",
    "core/store/src/trie/update.rs",
    "core/store/src/trie/update/iterator.rs",
    "core/store/src/trie/iterator.rs",
    "core/store/src/trie/trie_storage.rs",
    "core/store/src/trie/trie_storage_update.rs",
    "core/store/src/trie/trie_recording.rs",
    "core/store/src/trie/raw_node.rs",
    "core/store/src/trie/nibble_slice.rs",
    "core/store/src/trie/shard_tries.rs",
    "core/store/src/trie/config.rs",
    "core/store/src/trie/outgoing_metadata.rs",
    "core/store/src/trie/receipts_column_helper.rs",
    "core/store/src/trie/prefetching_trie_storage.rs",
    "core/store/src/trie/ops/insert_delete.rs",
    "core/store/src/trie/ops/interface.rs",
    "core/store/src/trie/ops/iter.rs",
    "core/store/src/trie/mem/lookup.rs",
    "core/store/src/trie/mem/memtrie_update.rs",
    "core/store/src/trie/mem/node/encoding.rs",
    "core/store/src/trie/mem/node/view.rs",
    "core/store/src/trie/mem/flexible_data/encoding.rs",
    "core/store/src/trie/mem/flexible_data/children.rs",
    "core/store/src/trie/mem/flexible_data/value.rs",
    "core/store/src/flat/storage.rs",
    "core/store/src/flat/chunk_view.rs",
    "core/store/src/flat/delta.rs",
    "core/store/src/adapter/trie_store.rs",
    "core/store/src/adapter/flat_store.rs",
    "core/store/src/contract.rs",

    # =================================================================================
    # Signature verification reachable from attacker-supplied transactions
    # =================================================================================
    "core/crypto/src/signature.rs",

    # =================================================================================
    # Public RPC entrypoints an unprivileged user can reach directly
    # =================================================================================
    "chain/jsonrpc/src/api/transactions.rs",
    "chain/jsonrpc/src/api/query.rs",
    "chain/jsonrpc/src/api/call_function.rs",
    "chain/jsonrpc/src/api/view_state.rs",
    "chain/jsonrpc/src/api/view_access_key.rs",
    "chain/jsonrpc/src/api/view_access_key_list.rs",
    "chain/jsonrpc/src/api/view_gas_key_nonces.rs",
    "chain/jsonrpc/src/api/receipts.rs",
    "chain/jsonrpc/src/api/changes.rs",
    "chain/jsonrpc/src/lib.rs",
]


target_scopes = [
    "Critical. An unprivileged attacker who can only submit signed transactions or deploy and call their own contracts can mint, duplicate, or steal NEAR tokens, breaking the total-supply or per-account balance invariant through deposit, refund, gas-refund, staking, storage-staking, or receipt-accounting paths.",
    "Critical. An unprivileged attacker can craft a transaction, receipt, or contract that makes chunk application panic, abort, hang, or consume unbounded memory or time on every validating node, stalling a shard or halting the chain.",
    "Critical. An unprivileged attacker can trigger nondeterministic or path-inconsistent execution so honest nodes disagree on state root, gas burn, or outcome for the same chunk, causing state divergence or an unintended chain split.",
    "Critical. An unprivileged attacker can act on an account they do not control by bypassing signature, nonce, or access-key authorization, FunctionCall access-key restrictions such as allowance, receiver_id and method_names, delegate-action sender binding or replay protection, or predecessor_id attribution.",
    "Critical. An unprivileged attacker can bypass gas metering or storage staking so compute, storage growth, receipt size, or recorded witness size is unaccounted or underpriced, obtaining free execution, unbounded state bloat, or validator resource exhaustion.",
    "High. An unprivileged attacker can bypass congestion control, bandwidth scheduling, or receipt and queue limits to indefinitely stall receipt delivery for a shard, or permanently strand cross-shard receipts and lock user funds.",
    "High. An unprivileged attacker can exploit serialization, trie-key, or account-id parsing differentials to collide storage keys across accounts, corrupt state accounting, or make validation and execution disagree about the same transaction.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one nearcore target.

    ```
    target_file format:
    "'File Name: runtime/runtime/src/actions.rs -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit and fuzzing questions for this exact nearcore target:

    {target_file}

    Project focus:
    nearcore is the NEAR Protocol reference client. Focus on transaction and receipt validation, action execution, access-key authorization, balance and gas accounting, storage staking, wasm preparation and metering, host functions, trie and state accounting, congestion and bandwidth limits, and determinism of chunk application.

    Rules:
    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Rust symbols (fn, struct, enum, field) when possible.
    * Attacker is unprivileged only: an ordinary account holder. They can submit signed transactions and meta-transactions through public RPC, deploy and call their own contracts, and fund their own accounts.
    * Attacker is NOT a validator, block or chunk producer, node operator, or peer. Ignore malicious-node, malicious-peer, P2P message, network-layer, node-config, CLI, leaked-key, and social-engineering assumptions.
    * Ignore test files, mocks, fuzz harnesses, docs, generated files, params-estimator, config-only findings, and dependency-only issues.
    * Ignore issues gated behind protocol features that are not yet enabled unless the path is reachable on the current protocol version.
    * Generate 12 to 16 high-signal questions.
    * At least 70% must target balance or supply invariants, gas or storage metering bypass, access-key and signer authorization, node panic or unbounded resource use, execution nondeterminism, or receipt and congestion accounting failures.
    * Every question must be testable by unit test, integration test, fuzz test, invariant test, or differential test.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Conservation: total token supply and per-account balances stay exact across transfers, refunds, gas refunds, staking, storage staking, and receipt processing. No mint, no loss.
    * Metering is complete: every unit of compute, memory, storage, receipt and witness growth is charged before it is performed, and charges cannot overflow, saturate, or be skipped.
    * Authorization is exact: only the account whose key signed a transaction may act, access-key restrictions hold, nonces are strictly increasing, and predecessor_id and signer_id cannot be forged.
    * Determinism and liveness: applying the same chunk yields the same state root, gas, and outcomes on every node, and no attacker-supplied input can panic, hang, or unboundedly grow a validator.
    * Progress is preserved: congestion control, bandwidth limits, and receipt queues bound resources without permanently stranding receipts or user funds.

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
    "[File: {target_file}] [Function: symbol_or_module] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: unit/integration/fuzz PARAMETERS and assert BALANCE_CONSERVATION, GAS_OR_STORAGE_METERING, AUTHORIZATION_BINDING, or DETERMINISM_AND_LIVENESS.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused nearcore exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: an ordinary account holder submitting transactions, meta-transactions, contract deploys, and contract calls through public RPC. No validator, chunk producer, node operator, peer, leaked key, or social engineering.
- Reject malicious-node, malicious-peer, P2P/network-layer, node-config, and operator-only paths.
- Reject anything that depends only on test/mock/fuzz-harness/docs/config/generated files, dependency bugs alone, direct store mutation from tests, or best-practice cleanup without exploitable impact.
- Focus on real protocol compromise paths: balance or supply violations, gas or storage metering bypass, authorization bypass, node panic or unbounded resource use, state divergence, and receipt or congestion accounting failures.

## Validate
- Trace the exact reachable path from the attacker-supplied transaction, action, receipt, contract, or RPC request into the affected function.
- Check whether existing validation, cost charging, limit checks, protocol-version gating, or overflow-checked arithmetic already stops it.
- Accept only real fund loss or inflation, free or underpriced execution or storage, unauthorized action on another account, chain stall or node crash, or state divergence.
- Require exact file/function support and a reproducible unit/integration/fuzz/invariant PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker inputs, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact and matching NEAR bounty impact class]

### Likelihood Explanation
[Preconditions, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Unit/integration test or fuzz/invariant test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for nearcore security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Reject malicious-node, malicious-peer, validator-only, P2P/network-layer, operator-only, leaked-key, dependency-only, docs/style, generated-file, test/mock/config-only, and purely theoretical issues.
- Reject if the exploit needs privileged access, victim social engineering, impossible setup, or behavior outside what an ordinary account can submit through public RPC.
- Reject if the bug was fixed, acknowledged, or publicly disclosed already, per the eligibility rules.
- A valid report must be triggerable by an unprivileged account, unless the claim proves privilege escalation from an unprivileged path.
- The final impact must map to an in-scope NEAR impact such as token inflation or theft, unauthorized state or balance modification, chain halt or shard stall, node crash or resource exhaustion from a submitted transaction, state divergence or chain split, or gas/storage metering bypass.
- Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken protocol assumption.
3. Reachable exploit path: preconditions -> attacker transaction/receipt/contract -> trigger -> bad result.
4. Existing checks, limits, and cost charging reviewed and shown insufficient.
5. Concrete in-scope impact with realistic likelihood and, where relevant, attacker cost far below damage.
6. Reproducible proof path: unit PoC, integration/test-loop test, invariant/fuzz test, or exact steps against a local node.
7. No obvious rejection reason from SECURITY.md, known issues, privilege assumptions, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can an ordinary account trigger this through normal transactions, contract calls, or RPC without validator or node access?
- Does the code actually behave as claimed on the current protocol version?
- Is the impact caused by this code, not by a malicious node, peer, validator, or dependency alone?
- Is the fund loss, inflation, unauthorized action, stall, crash, or divergence concrete, not hypothetical?
- Would a NEAR bounty triager accept the proof?
- What exact test would prove it?

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
[Concrete in-scope impact, severity rationale, and NEAR bounty category]

## Likelihood Explanation
[Attacker capability, required conditions, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or fuzz/invariant/integration test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for nearcore.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production repo context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-account analogs in transaction/receipt validation, action execution, access-key authorization, balance and gas accounting, storage staking, wasm metering, host functions, trie/state accounting, or congestion and bandwidth limits.
- Reject malicious-node, malicious-peer, validator-only, P2P/network-layer, mocked-only paths, dependency-only bugs, and no-impact analogs.

## Validate
- Map the bug class to the strongest reachable nearcore path from a submitted transaction, contract call, or RPC request.
- Prove root cause with exact file/function support.
- Accept only concrete token inflation or theft, unauthorized state or balance change, free or underpriced execution or storage, node panic or unbounded resource use, chain stall, or state divergence.

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
