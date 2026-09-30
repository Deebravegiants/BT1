import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 10
# todo: the path from https://github.com/rsksmart/rsk-powhsm
SOURCE_REPO = "rsksmart/rsk-powhsm"
# todo: the name of the repository
REPO_NAME = "rsk-powhsm"
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
    # =================================================================================
    # Signer command dispatch: APDU framing, command state machine, mode/reset handling
    # =================================================================================
    "firmware/src/powhsm/src/hsm.c",
    "firmware/src/powhsm/src/hsm.h",
    "firmware/src/powhsm/src/instructions.h",
    "firmware/src/powhsm/src/defs.h",
    "firmware/src/powhsm/src/err.h",
    "firmware/src/powhsm/src/flags.h",
    "firmware/src/powhsm/src/mem.c",
    "firmware/src/powhsm/src/mem.h",
    "firmware/src/powhsm/src/nvm.h",
    "firmware/src/powhsm/src/util.h",
    "firmware/src/powhsm/src/common_requirements.h",

    # =================================================================================
    # Peg-out signing authorization: BTC tx parsing, sighash, receipt, trie and
    # merkle proof checks, BIP44 path authorization
    # =================================================================================
    "firmware/src/powhsm/src/auth.c",
    "firmware/src/powhsm/src/auth.h",
    "firmware/src/powhsm/src/auth_constants.h",
    "firmware/src/powhsm/src/auth_tx.c",
    "firmware/src/powhsm/src/auth_tx.h",
    "firmware/src/powhsm/src/auth_receipt.c",
    "firmware/src/powhsm/src/auth_receipt.h",
    "firmware/src/powhsm/src/auth_trie.c",
    "firmware/src/powhsm/src/auth_trie.h",
    "firmware/src/powhsm/src/auth_path.c",
    "firmware/src/powhsm/src/auth_path.h",
    "firmware/src/powhsm/src/pathAuth.c",
    "firmware/src/powhsm/src/pathAuth.h",
    "firmware/src/powhsm/src/btctx.c",
    "firmware/src/powhsm/src/btctx.h",
    "firmware/src/powhsm/src/trie.c",
    "firmware/src/powhsm/src/trie.h",
    "firmware/src/powhsm/src/srlp.c",
    "firmware/src/powhsm/src/srlp.h",
    "firmware/src/powhsm/src/svarint.c",
    "firmware/src/powhsm/src/svarint.h",

    # =================================================================================
    # Blockchain bookkeeping: advanceBlockchain, PoW and merged-mining validation,
    # cumulative difficulty, brothers, ancestor proof, persisted best block state
    # =================================================================================
    "firmware/src/powhsm/src/bc.h",
    "firmware/src/powhsm/src/bc_advance.c",
    "firmware/src/powhsm/src/bc_advance.h",
    "firmware/src/powhsm/src/bc_ancestor.c",
    "firmware/src/powhsm/src/bc_ancestor.h",
    "firmware/src/powhsm/src/bc_block.h",
    "firmware/src/powhsm/src/bc_blockutils.h",
    "firmware/src/powhsm/src/bc_diff.c",
    "firmware/src/powhsm/src/bc_diff.h",
    "firmware/src/powhsm/src/bc_err.c",
    "firmware/src/powhsm/src/bc_err.h",
    "firmware/src/powhsm/src/bc_hash.c",
    "firmware/src/powhsm/src/bc_hash.h",
    "firmware/src/powhsm/src/bc_mm.c",
    "firmware/src/powhsm/src/bc_mm.h",
    "firmware/src/powhsm/src/bc_nu.h",
    "firmware/src/powhsm/src/bc_state.c",
    "firmware/src/powhsm/src/bc_state.h",

    # =================================================================================
    # Attestation and heartbeat: signed device/signer measurements over caller nonces
    # =================================================================================
    "firmware/src/powhsm/src/attestation.c",
    "firmware/src/powhsm/src/attestation.h",
    "firmware/src/powhsm/src/heartbeat.c",
    "firmware/src/powhsm/src/heartbeat.h",

    # =================================================================================
    # Ledger signer app entry and platform layer: seed and key derivation, endorsement,
    # NVM, hashing, APDU transport, exceptions
    # =================================================================================
    "firmware/src/ledger/signer/src/main.c",
    "firmware/src/ledger/signer/src/signer_ux.c",
    "firmware/src/ledger/signer/src/signer_ux.h",
    "firmware/src/hal/ledger/src/access.c",
    "firmware/src/hal/ledger/src/endorsement.c",
    "firmware/src/hal/ledger/src/hash.c",
    "firmware/src/hal/ledger/src/nvmem.c",
    "firmware/src/hal/ledger/src/platform.c",
    "firmware/src/hal/ledger/src/seed.c",
    "firmware/src/hal/common_linked/src/communication.c",
    "firmware/src/hal/common_linked/src/exceptions.c",
    "firmware/src/hal/common_linked/src/hash.c",
    "firmware/src/hal/common_linked/src/keccak256.c",
    "firmware/src/hal/common_linked/src/keccak256.h",
    "firmware/src/hal/common_linked/src/sha256.c",
    "firmware/src/hal/common_linked/src/sha256.h",
    "firmware/src/hal/include/hal/access.h",
    "firmware/src/hal/include/hal/communication.h",
    "firmware/src/hal/include/hal/constants.h",
    "firmware/src/hal/include/hal/endorsement.h",
    "firmware/src/hal/include/hal/exceptions.h",
    "firmware/src/hal/include/hal/hash.h",
    "firmware/src/hal/include/hal/log.h",
    "firmware/src/hal/include/hal/nvmem.h",
    "firmware/src/hal/include/hal/platform.h",
    "firmware/src/hal/include/hal/seed.h",

    # =================================================================================
    # Shared firmware primitives: big integer math, memory helpers, PIN policy,
    # APDU constants, compile-time checks, upgrade signer keys
    # =================================================================================
    "firmware/src/common/src/apdu.h",
    "firmware/src/common/src/bigdigits.c",
    "firmware/src/common/src/bigdigits.h",
    "firmware/src/common/src/bigdigits_helper.c",
    "firmware/src/common/src/bigdigits_helper.h",
    "firmware/src/common/src/bigdtypes.h",
    "firmware/src/common/src/compiletime.h",
    "firmware/src/common/src/eth.h",
    "firmware/src/common/src/ints.h",
    "firmware/src/common/src/memutil.h",
    "firmware/src/common/src/modes.h",
    "firmware/src/common/src/pin_policy.c",
    "firmware/src/common/src/pin_policy.h",
    "firmware/src/common/src/runtime.h",
    "firmware/src/common/src/upgrade_signers.h",
    "firmware/src/common/src/upgrade_signers/aleph.h",
    "firmware/src/common/src/upgrade_signers/bet.h",

    # =================================================================================
    # Ledger UI/bootloader (RSK-authored): signer authorization N-of-M, unlock, PIN,
    # onboarding, UI-side attestation and heartbeat, UI APDU handling
    # =================================================================================
    "firmware/src/ledger/ui/src/main.c",
    "firmware/src/ledger/ui/src/bootloader.c",
    "firmware/src/ledger/ui/src/bootloader.h",
    "firmware/src/ledger/ui/src/signer_authorization.c",
    "firmware/src/ledger/ui/src/signer_authorization.h",
    "firmware/src/ledger/ui/src/signer_authorization_status.c",
    "firmware/src/ledger/ui/src/signer_authorization_status.h",
    "firmware/src/ledger/ui/src/unlock.c",
    "firmware/src/ledger/ui/src/unlock.h",
    "firmware/src/ledger/ui/src/pin.c",
    "firmware/src/ledger/ui/src/pin.h",
    "firmware/src/ledger/ui/src/onboard.c",
    "firmware/src/ledger/ui/src/onboard.h",
    "firmware/src/ledger/ui/src/attestation.c",
    "firmware/src/ledger/ui/src/attestation.h",
    "firmware/src/ledger/ui/src/ui_heartbeat.c",
    "firmware/src/ledger/ui/src/ui_heartbeat.h",
    "firmware/src/ledger/ui/src/ui_comm.c",
    "firmware/src/ledger/ui/src/ui_comm.h",
    "firmware/src/ledger/ui/src/ui_err.h",
    "firmware/src/ledger/ui/src/ui_instructions.h",
    "firmware/src/ledger/ui/src/ux_handlers.c",
    "firmware/src/ledger/ui/src/ux_handlers.h",
    "firmware/src/ledger/ui/src/defs.h",
    "firmware/src/ledger/ui/src/common_requirements.h",
]


target_scopes = [
    "Critical. An ordinary Rootstock user makes the signer sign a BTC peg-out without a real, confirmed peg-out receipt: validate_merkle_proof, process_merkle_proof, trie_consume / trie_cb, rlp_consume / srlp, auth_sign_handle_merkleproof and auth_sign_handle_receipt let a crafted receipt, trie node sequence, RLP length or merkle proof (shortened path, node reused as leaf, hash of an inner node accepted as a receipt, mismatch between proved root and ancestor_receipts_root) pass, so funds leave the federation without a matching peg-out request.",
    "Critical. A user deploys a contract or crafts a transaction whose receipt is accepted as a genuine Bridge peg-out event: auth_receipt.c event address, topic and data checks, log index/selection, receipt type or status handling, and the release_request_* fields let a log emitted by any other contract, a failed transaction, a wrong topic, a duplicated or reordered log, or attacker-controlled data bytes stand in for the Bridge event and authorize a BTC transaction hash the user chose.",
    "Critical. The BTC transaction the signer signs differs from what the receipt authorizes: auth_sign_handle_btctx, btctx_consume / btctx_cb, svarint_consume, generate_message_to_sign, write_uint64_be, the input index, witnessScript and outpointValue fields let a peg-out with crafted output count, varint encoding, output script, amount, extra outputs, segwit marker/flag, locktime, sequence or multiple inputs be signed with a different sighash, amount or destination than the peg-out event committed to, or let the same input be signed under a wrong outpointValue.",
    "Critical. A forged or under-worked chain becomes the signer's trusted best_block: bc_advance, bc_adv_accum_diff, bc_adv_prologue, bc_adv_success, cap_block_difficulty, validate_mm_hash, validate_cb_txn_hash, compute_cb_txn_hash, patch_hash_for_mm, bc_mm_header_received, bc_diff and the brothers handling let a merge-mined header with a manipulated coinbase, merkle proof, mm hash prefix, difficulty field, uncle list (duplicates, wrong parent, count) or network-upgrade field count cumulative difficulty it did not earn, skip PoW on a block, or move best_block onto a fork the attacker's blocks can then be proved against.",
    "Critical. The ancestor proof binds a receipt to a block that is not in the signer's best chain: bc_upd_ancestor, bc_init_upd_ancestor, bc_upd_ancestor_prologue, bc_upd_ancestor_success, the ancestor_block / ancestor_receipts_root pair, bc_state persistence, bc_backup_partial_state and bc_reset_state let a block with the same height on a side chain, a header whose receipts root is swapped, a partially updated state after a failed advance or reset, or a stale ancestor after best_block moved be accepted, so a receipt from an orphaned or never-confirmed block authorizes signing.",
    "Critical. A peg-out is signed twice, out of order, or across a state gap: hsm_process_command, hsm_process_apdu, auth_transition_to, auth_sign, check_state, reset_shared_state, hsm_reset_if_starting and the sign / advance / updateAncestor / reset command sequence let interleaved or repeated commands reuse a validated receipt or ancestor for a second, different BTC transaction, keep authorization alive after resetAdvanceBlockchain or an error, or run a sign with half-initialized auth or bc state.",
    "Critical. The signer signs with the wrong key or leaks key material: auth_sign_handle_path, pathRequireAuth / pathDontRequireAuth, the BIP44 keyId to key mapping (BTC, tBTC vs RSK, MST), the authorized vs non-authorized sign formats, getPubKey, hal/ledger seed.c key derivation and access.c let a keyId string or path with odd length, extra components or a case/prefix variant sign an arbitrary hash with a BTC federation key without receipt authorization, or return private or seed-derived material.",
    "Critical. The attestation or heartbeat signature is forged or misused as a signing oracle: get_attestation, get_heartbeat, hash_public_key, the caller-supplied user-defined value and nonce, the endorsement in hal/ledger endorsement.c, keccak256 and sha256 helpers, double_sha256_rev and the UI-side attestation and ui_heartbeat let a chosen nonce, length or format make the device sign attacker-shaped data with a device or signer key, replay a stale measurement, or present an unauthorized signer as authentic.",
    "Critical. Integer, length or state bugs in the parsers turn a user-influenced peg-out or block into unauthorized signing or key exposure (not a crash or memory exhaustion): srlp.c, svarint.c, trie.c, btctx.c, auth_receipt.c, bc_advance.c, bigdigits.c, memutil.h, mem.c and communication.c length, offset and chunk arithmetic (wrap, truncation, signed/unsigned mix, chunk boundary between APDUs) let a valid-looking payload overwrite or read adjacent auth, bc or key state, flip a validated flag, or make a check compare the wrong bytes.",
    "Critical/High blind spot. An ordinary user exploits an assumption powHSM never wrote down: a receipt or trie field the firmware trusts because the honest node always builds it a certain way; a check present in the BTC sign path but missing for the RSK/MST hash path or the heartbeat; a constant (bridge address, event signature, minimum difficulty, confirmation depth, network upgrade activation) that differs between mainnet and the compiled configuration; an NVM write interrupted or reordered so best_block or the authorized signer hash is stale; an error path that leaves a validated flag set; or a peg-out edge (zero or dust amount, maximum value, many inputs, witnessScript shape) the format checks only cover in the common case - yielding theft of federation funds, permanently frozen funds or seed/key extraction.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one powHSM target.

    ```
    target_file format:
    "'File Name: firmware/src/powhsm/src/auth_receipt.c -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit questions for this exact powHSM target:

    {target_file}

    Project focus:
    RSK powHSM is the C firmware (Ledger signer, UI/bootloader and HAL) that holds the Rootstock PowPeg federation keys and signs BTC peg-out transactions. It signs a BTC tx only if the host proves the peg-out is real: a Rootstock receipt (trie/RLP/merkle proof) whose root matches ancestor_receipts_root, an ancestor block proved to be in the best chain the device tracks itself by verifying merge-mined PoW (advanceBlockchain: headers, brothers, cumulative difficulty, best_block in NVM), and a BTC tx/sighash that matches the event. Other commands: getPubKey, RSK/MST hash signing, attestation, heartbeat, reset. Data reaches the device through an honest powpeg-node and middleware on the same host.

    Rules:
    * Treat `File Name:` as the exact file and `Scope:` as the ONLY impact to target.
    * Assume full repo context. Do not ask for code or say anything is missing.
    * Use exact C symbols (function, struct, field, macro, error code) when possible.
    * Attacker is unprivileged only: an ordinary Rootstock user or contract deployer who creates peg-out requests, transactions, receipts and logs; a miner limited to producing valid-PoW block content (headers, uncles, merged-mining fields) without majority hashrate; a BTC user whose UTXOs or outputs appear in peg-out flows. Their data reaches the HSM through an honest node.
    * Attacker is NOT a malicious peer, malicious node or middleware, not a federation member, not a firmware/signer authorizer, has no physical or local access to the Ledger device or host, holds no keys or PIN. Never assume a malicious host, leaked key or social engineering.
    * Out of scope, never ask about: Ledger devices and their physical security, Ledger company code (bolos_ux_*, seed onboarding), TCPSigner, hal/x86, SGX code, middleware and tooling, tests, DoS by local access, findings that do not allow arbitrary or insecure use of the keys derived from the device seed.
    * Ignore test files, mocks, fuzz harnesses, build and generated code.
    * Every question must be a real scenario an ordinary user can cause on the live network: concrete peg-out/receipt/block/tx content, the exact command sequence the honest node then sends, and the state the device is in. No unbounded-loop, memory-exhaustion, CPU or "huge input" questions.
    * Generate 40 to 80 high-signal questions, at least 70% aimed at Critical impact. No generic checklist items or repeated root causes.
    * Every question must be testable with the firmware unit tests or the middleware/TCPSigner harness against the same C code, or a fuzz/property test.

    Core invariants:
    * Authorization: a BTC signature exists only for a tx whose outputs and amounts match a Bridge peg-out event in a receipt proved against the current ancestor_receipts_root.
    * Chain: best_block, ancestor and receipts root only move through fully validated PoW with sufficient cumulative difficulty; a partial or failed update never leaves usable state.
    * Binding: one proof authorizes exactly the tx and input it was checked against; no replay or reuse across resets.
    * Keys: each keyId signs only in its own format; no seed or private key material leaves the device.

    Each question must include:
    1. target function;
    2. attacker action (what the user or miner creates on-chain);
    3. preconditions (device state, best_block, ancestor, key id);
    4. command sequence the honest node sends;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS cause COMMAND_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: test PARAMETERS and assert AUTHORIZATION, CHAIN, BINDING, or KEYS.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused powHSM exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: an ordinary Rootstock user or contract deployer (peg-out requests, transactions, receipts, logs), a miner limited to valid-PoW block content, or a BTC user whose outputs appear in peg-outs, with data relayed by an honest node.
- Reject malicious peer/node/middleware, federation members, signer authorizers, physical or local device access, leaked keys/PIN and social engineering.
- Reject Ledger devices and physical security, Ledger company code, TCPSigner, hal/x86, SGX, middleware/tooling, tests/mocks/fuzz code, and anything that does not allow arbitrary or insecure use of the seed-derived keys.
- Reject unbounded-loop, memory-exhaustion, CPU and local-access DoS claims.
- Focus on real impact: theft of federation/user funds via unauthorized signing, permanent freezing of funds, protocol insolvency, remote extraction of seed or private keys, taking authenticated actions on behalf of others.

## Validate
- Trace the exact path from the on-chain data the attacker creates through the APDU commands to the firmware check that fails.
- Check existing guards: auth state transitions, receipt/trie/merkle validation against ancestor_receipts_root, bc_advance PoW/difficulty/mm checks, bc_state resets, path authorization, tx/sighash binding, length and bounds checks in srlp/svarint/trie/btctx.
- Confirm the path is reachable in the production (Ledger mainnet) build, not only in test or TCPSigner builds.
- Accept only concrete unauthorized signing, key exposure, frozen funds or insolvency.
- Require exact file/function support and a reproducible PoC (unit test or harness run).

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker-created data, command sequence, and why existing checks fail]

### Impact Explanation
[Concrete impact and severity, per the RootstockLabs Immunefi program]

### Likelihood Explanation
[Preconditions, attacker cost, device state, feasibility, repeatability]

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
    Generate a short cross-project analog scan prompt for powHSM.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production firmware only: firmware/src/powhsm, firmware/src/ledger/signer, firmware/src/hal/ledger, firmware/src/hal/common_linked, firmware/src/hal/include, firmware/src/common, and the RSK-authored firmware/src/ledger/ui files. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint. The analog must stand on powHSM's own code.
- Keep only analogs an unprivileged party can reach: an ordinary Rootstock user/contract deployer (receipts, logs, peg-out data), a valid-PoW miner (header, uncle and merged-mining content), or a BTC user, with data forwarded by an honest node. No malicious peer/node, federation member, physical or local access.
- Map the class onto powHSM's real shape:
  * proof verification: RLP/trie/merkle receipt proofs checked against ancestor_receipts_root (second-preimage, node-as-leaf, path length, hash-of-inner-node, prefix ambiguity);
  * event authentication: Bridge address/topic/data matching in a receipt, spoofed logs, failed txs, receipt types;
  * signing binding: BTC tx parsing, varint and script handling, sighash construction, outpointValue, input index, segwit serialization, tx malleability;
  * light-client PoW: merged-mining header and coinbase proof, cumulative difficulty, difficulty cap, uncles/brothers, fork choice, network-upgrade fields, checkpoint/initial block;
  * state machine: multi-APDU command sequences, chunked input, partial update rollback, replay, stale ancestor, NVM persistence and power-cut ordering;
  * key handling: BIP44 path parsing and authorization, derivation, keyId-to-format mapping, key/seed exposure through outputs, logs or uninitialized buffers;
  * attestation/heartbeat: caller nonces signed by device keys, signing-oracle and replay risks;
  * C hazards that yield unauthorized signing or key leak: integer wrap/truncation, signed-unsigned mix, off-by-one, uninitialized data, TOCTOU across APDUs, constant-time comparison of secrets/PINs.
- Reject privileged, physical, local, leaked-key, tests/mocks, TCPSigner, hal/x86, SGX, Ledger company code, middleware/tooling, unbounded-loop/memory/DoS, and no-impact analogs.
- Critical, High and Medium only, and only when it allows arbitrary or insecure use of the seed-derived keys or concrete fund loss or freezing.

## Validate
- Map the class to the strongest path an ordinary user or miner can create on-chain, naming the exact command sequence and data fields.
- Prove root cause with exact file/function support.
- Accept only unauthorized signing/theft of funds, permanent freezing of funds, protocol insolvency, seed or key extraction, or a concrete HSM-caused stall of valid peg-out signing.

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
    Generate a strict bounty-style validation prompt for powHSM security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and RESEARCHER.md for scope, exclusions, and valid impact classes.
- Scope is the Immunefi RootstockLabs program, PowHSM asset (Blockchain/DLT, rsk-powhsm latest release): the Ledger firmware in firmware/src/powhsm, firmware/src/ledger, firmware/src/hal/ledger, firmware/src/hal/common_linked, firmware/src/hal/include and firmware/src/common. Primacy of Impact applies to Critical/High.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the evidence proves the higher impact.
- Accepted impacts: Critical (remote extraction of HSM seed or private keys; direct theft of user funds; permanent freezing of funds; protocol insolvency; taking authenticated actions on behalf of others without their interaction). High and Medium only if the program lists them for Blockchain/DLT and the HSM itself causes them (for example a concrete, non-DoS stall of valid peg-out signing or corrupted chain state). Reject Low, informational and best-practice findings.
- Impact must allow arbitrary or insecure use of the keys derived from the device seed, or concrete loss/freezing of funds.
- Reject Ledger devices and their physical security, Ledger company source code (until the 90-day period), TCPSigner, firmware/src/hal/x86, SGX code, middleware and tooling, tests/mocks/fuzz, DoS by physical or local access, and DoS in general.
- Reject anything needing leaked keys or credentials, phishing or social engineering, a malicious peer/node/middleware or host (HSM, middleware and powpeg-node run on the same host with no external exposure), federation member or signer-authorizer collusion, or attacks the reporter already exploited themselves.
- Reject if the exploit needs more than an unprivileged Rootstock user, contract deployer, valid-PoW miner without majority hashrate, or BTC user, with data relayed by an honest node.
- Reject if already fixed, acknowledged, in the audit report (audits/), or public. A runnable PoC on a local build is mandatory; prefer #NoVulnerability over speculation.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references in the production Ledger build.
2. Clear root cause and a broken invariant (authorization, chain validity, tx binding, key isolation) from docs/ (protocol.md, blockchain-bookkeeping.md, attestation.md, signer-authorization.md).
3. Reachable path: attacker-created on-chain data -> honest node's APDU sequence -> device state -> bad result.
4. Existing guards reviewed and shown insufficient: auth state machine, receipt/trie/merkle checks, ancestor root binding, bc_advance PoW/difficulty/mm checks, path authorization, sighash binding, bounds and length checks, NVM state handling.
5. Concrete accepted impact with realistic likelihood.
6. Reproducible PoC (unit test, harness run, or crafted command sequence).
7. No rejection reason from SECURITY.md, the program exclusions, or privilege assumptions.

## Silent Triage Questions
Before output, internally answer:
- Can an ordinary user or miner trigger this with no key, no PIN and no control of the node?
- Does it work in the Ledger production build, not just TCPSigner or tests?
- Is the impact caused by powHSM firmware, not Ledger's code or the device hardware?
- Does it allow arbitrary or insecure use of seed-derived keys, or concrete fund loss?
- What exact test proves it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the bug and impact]

## Finding Description
[Exact code path, root cause, exploit flow, and why existing guards fail]

## Impact Explanation
[Concrete impact, severity, and Immunefi impact category]

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
