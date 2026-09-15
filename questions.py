import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 25
# todo: the path from https://github.com/polytope-labs/hyperbridge
SOURCE_REPO = "polytope-labs/hyperbridge"
# todo: the name of the repository
REPO_NAME = "hyperbridge"
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
    # EVM host: the permissionless dispatch and delivery surface on every connected chain
    # =================================================================================
    "evm/src/core/EvmHost.sol",
    "evm/src/core/HandlerV2.sol",
    "evm/src/core/HostManager.sol",
    "evm/src/utils/CallDispatcher.sol",
    "sdk/packages/core/contracts/libraries/Message.sol",
    "sdk/packages/core/contracts/libraries/StateMachine.sol",
    "sdk/packages/core/contracts/interfaces/IDispatcher.sol",
    "sdk/packages/core/contracts/interfaces/IHost.sol",
    "sdk/packages/core/contracts/interfaces/IHandlerV2.sol",
    "sdk/packages/core/contracts/interfaces/IApp.sol",
    "sdk/packages/core/contracts/interfaces/ICallDispatcher.sol",
    "sdk/packages/core/contracts/apps/HyperApp.sol",

    # =================================================================================
    # EVM consensus verification: the only thing standing between a proof and a state root
    # =================================================================================
    "evm/src/consensus/EcdsaBeefy.sol",
    "evm/src/consensus/SP1Beefy.sol",
    "evm/src/consensus/ConsensusRouter.sol",
    "evm/src/consensus/Codec.sol",
    "evm/src/consensus/Types.sol",
    "sdk/packages/core/contracts/interfaces/IConsensusV2.sol",

    # =================================================================================
    # EVM apps custodying user funds: token bridge, intents, bandwidth, paymaster, oracle
    # =================================================================================
    "sdk/packages/core/contracts/apps/HyperFungibleToken.sol",
    "sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol",
    "sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol",
    "sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol",
    "sdk/packages/core/contracts/interfaces/IHyperFungibleToken.sol",
    "evm/src/utils/HyperFungibleTokenImpl.sol",
    "evm/src/apps/IntentGatewayV2.sol",
    "evm/src/apps/intentsv2/IntentsBase.sol",
    "evm/src/apps/intentsv2/ExtrinsicIntents.sol",
    "evm/src/apps/intentsv2/IntrinsicIntents.sol",
    "evm/src/apps/intentsv2/SolverAccount.sol",
    "sdk/packages/core/contracts/apps/IntentGatewayV2.sol",
    "sdk/packages/core/contracts/apps/IntentPriceOracle.sol",
    "evm/src/apps/BandwidthManager.sol",
    "evm/src/utils/SimplexPaymaster.sol",
    "evm/src/utils/VWAPOracle.sol",
    "evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol",
    "evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol",
    "evm/src/utils/uniswapv2/GnosisUniswapV2Wrapper.sol",
    "sdk/packages/core/contracts/vaults/StreamingYieldVault.sol",
    "sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol",

    # =================================================================================
    # ISMP core: message identity, commitments, and the request/response/timeout handlers
    # =================================================================================
    "modules/ismp/core/src/handlers.rs",
    "modules/ismp/core/src/handlers/request.rs",
    "modules/ismp/core/src/handlers/response.rs",
    "modules/ismp/core/src/handlers/timeout.rs",
    "modules/ismp/core/src/handlers/consensus.rs",
    "modules/ismp/core/src/messaging.rs",
    "modules/ismp/core/src/router.rs",
    "modules/ismp/core/src/dispatcher.rs",
    "modules/ismp/core/src/consensus.rs",
    "modules/ismp/core/src/host.rs",
    "modules/ismp/core/src/module.rs",
    "modules/ismp/core/src/abi.rs",
    "modules/ismp/core/src/events.rs",
    "modules/ismp/core/src/error.rs",

    # =================================================================================
    # pallet-ismp: the unsigned extrinsic anyone submits to move messages through Hyperbridge
    # =================================================================================
    "modules/pallets/ismp/src/lib.rs",
    "modules/pallets/ismp/src/impls.rs",
    "modules/pallets/ismp/src/child_trie.rs",
    "modules/pallets/ismp/src/dispatcher.rs",
    "modules/pallets/ismp/src/fee_handler.rs",
    "modules/pallets/ismp/src/host.rs",
    "modules/pallets/ismp/src/utils.rs",
    "modules/pallets/ismp/src/events.rs",
    "modules/pallets/ismp/src/errors.rs",
    "modules/pallets/ismp/src/offchain.rs",
    "modules/pallets/call-decompressor/src/lib.rs",

    # =================================================================================
    # MMR: the accumulator whose root every outbound Hyperbridge message is proven against
    # =================================================================================
    "modules/pallets/mmr/src/lib.rs",
    "modules/pallets/mmr/src/mmr/mmr.rs",
    "modules/pallets/mmr/src/mmr/mod.rs",
    "modules/pallets/mmr/src/mmr/storage.rs",
    "modules/pallets/mmr/primitives/src/lib.rs",
    "modules/pallets/beefy-consensus-proofs/src/lib.rs",
    "modules/pallets/beefy-consensus-proofs/src/types.rs",

    # =================================================================================
    # Hyperbridge pallets holding user balances, relayer fees and cross-chain accounting
    # =================================================================================
    "modules/pallets/hyper-fungible-token/src/lib.rs",
    "modules/pallets/hyper-fungible-token/src/module.rs",
    "modules/pallets/hyper-fungible-token/src/impls.rs",
    "modules/pallets/hyper-fungible-token/src/types.rs",
    "modules/pallets/hyper-fungible-token/src/error.rs",
    "modules/pallets/relayer/src/lib.rs",
    "modules/pallets/relayer/src/accumulate.rs",
    "modules/pallets/relayer/src/withdrawal.rs",
    "modules/pallets/relayer/src/outbound_request.rs",
    "modules/pallets/relayer/src/outbound_consensus.rs",
    "modules/pallets/messaging-incentives/src/lib.rs",
    "modules/pallets/consensus-incentives/src/lib.rs",
    "modules/pallets/consensus-incentives/src/impls.rs",
    "modules/pallets/intents-coprocessor/src/lib.rs",
    "modules/pallets/intents-coprocessor/src/types.rs",
    "modules/pallets/state-coprocessor/src/lib.rs",
    "modules/pallets/state-coprocessor/src/impls.rs",
    "modules/pallets/bandwidth/src/lib.rs",
    "modules/pallets/bandwidth/src/abi.rs",
    "modules/pallets/bandwidth/src/types.rs",
    "modules/pallets/fishermen/src/lib.rs",
    "modules/pallets/fishermen/src/extension.rs",
    "modules/pallets/host-executive/src/lib.rs",
    "modules/pallets/collator-manager/src/lib.rs",

    # =================================================================================
    # Consensus clients: anyone may submit a consensus update for any tracked chain
    # =================================================================================
    "modules/ismp/clients/beefy/src/lib.rs",
    "modules/ismp/clients/beefy/src/consensus.rs",
    "modules/ismp/clients/grandpa/src/lib.rs",
    "modules/ismp/clients/grandpa/src/consensus.rs",
    "modules/ismp/clients/grandpa/src/messages.rs",
    "modules/ismp/clients/parachain/client/src/lib.rs",
    "modules/ismp/clients/parachain/client/src/consensus.rs",
    "modules/ismp/clients/sync-committee/src/lib.rs",
    "modules/ismp/clients/sync-committee/src/pallet.rs",
    "modules/ismp/clients/sync-committee/src/beacon_client.rs",
    "modules/ismp/clients/sync-committee/src/types.rs",
    "modules/ismp/clients/casper-ffg/src/lib.rs",
    "modules/ismp/clients/bsc/src/lib.rs",
    "modules/ismp/clients/bsc/src/pallet.rs",
    "modules/ismp/clients/optimism/src/lib.rs",
    "modules/ismp/clients/ismp-optimism/src/lib.rs",
    "modules/ismp/clients/ismp-optimism/src/pallet.rs",
    "modules/ismp/clients/arbitrum/src/lib.rs",
    "modules/ismp/clients/ismp-arbitrum/src/lib.rs",
    "modules/ismp/clients/ismp-arbitrum/src/pallet.rs",
    "modules/ismp/clients/polygon/src/lib.rs",
    "modules/ismp/clients/tendermint/src/lib.rs",
    "modules/ismp/clients/tendermint/src/pallet.rs",
    "modules/ismp/clients/pharos/src/lib.rs",

    # =================================================================================
    # Consensus verifiers: signature, threshold, fork and finality checks on submitted proofs
    # =================================================================================
    "modules/consensus/beefy/verifier/src/lib.rs",
    "modules/consensus/beefy/verifier/src/sp1.rs",
    "modules/consensus/beefy/primitives/src/lib.rs",
    "modules/consensus/grandpa/verifier/src/lib.rs",
    "modules/consensus/grandpa/primitives/src/lib.rs",
    "modules/consensus/grandpa/primitives/src/justification.rs",
    "modules/consensus/sync-committee/verifier/src/lib.rs",
    "modules/consensus/sync-committee/verifier/src/crypto.rs",
    "modules/consensus/sync-committee/primitives/src/lib.rs",
    "modules/consensus/sync-committee/primitives/src/types.rs",
    "modules/consensus/sync-committee/primitives/src/util.rs",
    "modules/consensus/sync-committee/primitives/src/ssz/mod.rs",
    "modules/consensus/sync-committee/primitives/src/ssz/byte_list.rs",
    "modules/consensus/sync-committee/primitives/src/consensus_types.rs",
    "modules/consensus/bsc/verifier/src/lib.rs",
    "modules/consensus/bsc/verifier/src/primitives.rs",
    "modules/consensus/tendermint/verifier/src/lib.rs",
    "modules/consensus/tendermint/verifier/src/verifier.rs",
    "modules/consensus/tendermint/verifier/src/hashing.rs",
    "modules/consensus/tendermint/primitives/src/verifier.rs",
    "modules/consensus/tendermint/ics23-primitives/src/lib.rs",
    "modules/consensus/pharos/verifier/src/lib.rs",
    "modules/consensus/pharos/verifier/src/state_proof.rs",
    "modules/consensus/pharos/primitives/src/spv.rs",
    "modules/consensus/geth-primitives/src/lib.rs",

    # =================================================================================
    # State proof verification: membership and non-membership behind every delivered message
    # =================================================================================
    "modules/ismp/state-machines/evm/src/lib.rs",
    "modules/ismp/state-machines/evm/src/utils.rs",
    "modules/ismp/state-machines/evm/src/types.rs",
    "modules/ismp/state-machines/evm/src/presets.rs",
    "modules/ismp/state-machines/evm/src/substrate_evm.rs",
    "modules/ismp/state-machines/evm/src/tendermint.rs",
    "modules/ismp/state-machines/substrate/src/lib.rs",
    "modules/ismp/state-machines/pharos/src/lib.rs",
    "modules/trees/ethereum/src/lib.rs",
    "modules/trees/ethereum/src/node_codec.rs",
    "modules/trees/ethereum/src/storage_proof.rs",
    "modules/utils/crypto/src/lib.rs",
    "modules/utils/bls-utils/src/lib.rs",

    # =================================================================================
    # Runtime wiring: module routing, fee config and consensus client registration
    # =================================================================================
    "parachain/runtimes/nexus/src/ismp.rs",
    "parachain/runtimes/gargantua/src/ismp.rs",
]


target_scopes = [
    "Critical. An attacker delivers a cross-chain message that was never dispatched on the claimed source chain, letting them mint or withdraw funds from any Hyperbridge app: handlePostRequests and handleGetResponses in evm/src/core/HandlerV2.sol, dispatchIncoming and requestReceipts in evm/src/core/EvmHost.sol, encode and hash in sdk/packages/core/contracts/libraries/Message.sol, handle in modules/ismp/core/src/handlers/request.rs and response.rs, verify_membership and verify_state_proof in modules/ismp/state-machines/evm/src/lib.rs, or trie node decoding in modules/trees/ethereum/src/storage_proof.rs and node_codec.rs accept a proof whose storage key, slot layout, source StateMachine or commitment does not actually bind to a real dispatched request.",
    "Critical. An attacker submits a consensus proof that installs an attacker-chosen state root, so every subsequent message proof against it verifies and all bridged funds become stealable: verify, verifyMmrUpdateProof, verifyMmrLeaf, verifyParachainHeaderProof, leafIndex and checkParticipationThreshold in evm/src/consensus/EcdsaBeefy.sol, verifyConsensus in SP1Beefy.sol, verify in ConsensusRouter.sol, update_client in modules/ismp/core/src/handlers/consensus.rs, verify_sync_committee_attestation in modules/consensus/sync-committee/verifier/src/lib.rs, or the verifiers in modules/consensus/beefy, grandpa, bsc, tendermint and pharos mishandle signature aggregation, participation thresholds, authority-set rotation, fork versions or MMR leaf indexing on a self-supplied proof.",
    "Critical. The cross-chain token supply stops being conserved, so an attacker mints unbacked tokens or a victim's deposit is burned without a payout: send, onAccept and onPostRequestTimeout in sdk/packages/core/contracts/apps/HyperFungibleToken.sol and WrappedHyperFungibleToken.sol, evm/src/utils/HyperFungibleTokenImpl.sol, the OnAccept, OnResponse and OnTimeout impls in modules/pallets/hyper-fungible-token/src/module.rs, and convert_to_balance and convert_to_erc20 in impls.rs let asset id, decimals, redeem flag or beneficiary be chosen so the burn on one side and the mint on the other do not match.",
    "Critical. An attacker drains intent escrow without delivering the promised outputs, or blocks a solver from ever being paid for a fill they performed: placeOrder, fillOrder, cancelOrder and select in evm/src/apps/IntentGatewayV2.sol, _execute, _withdraw, _select, _sweepDust, _calculateCommitmentSlotHash and DOMAIN_SEPARATOR in evm/src/apps/intentsv2/IntentsBase.sol, ExtrinsicIntents.sol, IntrinsicIntents.sol and SolverAccount.sol, place_bid and retract_bid in modules/pallets/intents-coprocessor/src/lib.rs, or recordSpread and onAccept in evm/src/utils/VWAPOracle.sol let an order commitment, fill proof, bid or price feed be forged, replayed or reused across chains and deployments.",
    "Critical. The timeout path pays out for a message that was in fact delivered, or refuses to pay out for one that never was, letting an attacker double-spend escrowed value: handlePostRequestTimeouts and handleGetRequestTimeouts in evm/src/core/HandlerV2.sol, dispatchTimeOut in evm/src/core/EvmHost.sol, handle in modules/ismp/core/src/handlers/timeout.rs, timed_out and get_timeout in modules/ismp/core/src/router.rs, verify_non_membership in modules/ismp/state-machines/evm/src/lib.rs and substrate/src/lib.rs, or the receipt lookups they rely on treat an absent receipt, a zero timeout, or a proof taken at an attacker-chosen height as proof of non-delivery.",
    "Critical. An attacker claims relayer fees, incentives or protocol balances they never earned, or makes an honest relayer's accrued fees unwithdrawable: accumulate_fees and withdraw_fees in modules/pallets/relayer/src/lib.rs, withdraw and message in withdrawal.rs, claim_outbound_request_delivery_reward and claim_outbound_consensus_delivery_reward with outbound_request.rs and outbound_consensus.rs, accumulate.rs fee crediting, fee_handler.rs and fund_message in modules/pallets/ismp/src, recordEpoch and relayerOf in evm/src/core/EvmHost.sol, or modules/pallets/messaging-incentives and consensus-incentives credit a self-declared relayer address, double-count a delivery, or let a withdrawal be replayed on another chain.",
    "Critical. An attacker impersonates a trusted peer module or the host itself, so an app executes privileged cross-chain instructions on attacker calldata: the restrict and notFrozen modifiers, updateHostParams, withdraw, setFrozenState and _bytesToAddress in evm/src/core/EvmHost.sol, onAccept in evm/src/core/HostManager.sol, dispatch in evm/src/utils/CallDispatcher.sol, sdk/packages/core/contracts/apps/HyperApp.sol source and sender checks, onAccept and purchase in evm/src/apps/BandwidthManager.sol, onAccept and _validatePaymasterUserOp in evm/src/utils/SimplexPaymaster.sol, or the Router and module id resolution in parachain/runtimes/nexus/src/ismp.rs and modules/ismp/core/src/module.rs fail to bind a delivered request to the exact source chain and source module allowed to send it.",
    "Critical. Hyperbridge's own outbound commitments are corrupted, so a proof verifies for a message that was never dispatched or an honestly dispatched message can never be proven: push, finalize and generate_proof in modules/pallets/mmr/src/lib.rs with mmr/mmr.rs and mmr/storage.rs, request and response commitment keys in modules/pallets/ismp/src/child_trie.rs, the dispatcher in modules/pallets/ismp/src/dispatcher.rs, handle_unsigned in modules/pallets/state-coprocessor/src/lib.rs and impls.rs, or modules/pallets/beefy-consensus-proofs/src/lib.rs let an attacker's dispatched request collide with, displace or be omitted from the leaf set the BEEFY root commits to.",
    "High. A single attacker-submitted message or consensus update permanently stops a route from delivering messages, freezing user funds already in flight: update_client and freeze_client in modules/ismp/core/src/handlers/consensus.rs, insert_bounded_state_commitment, insert_bounded_update_time, state_machine_commitment_cap and update_commitment_caps in modules/pallets/ismp/src/lib.rs, storeStateMachineCommitment, deleteStateMachineCommitment and setFrozenState in evm/src/core/EvmHost.sol, veto_state_commitment, blacklist_dispute_game and blacklist_arbitrum_claim in modules/pallets/fishermen/src/lib.rs, or the height and timestamp monotonicity checks in the sync-committee, bsc, arbitrum, optimism and parachain clients let a client be wedged, rolled back or evicted so no later proof can ever be accepted.",
    "Critical/High blind spot. An ordinary message dispatcher, relayer, token bridger or intent solver abuses an assumption Hyperbridge never wrote down: a commitment that is unique under one encoding but collides under abi.rs versus Message.sol or across GET and POST, a StateMachine identifier that two distinct chains can both encode to, a proof checked against one state root but consumed after a newer or vetoed commitment replaced it, a fee, nonce or receipt read again after the check that authorized it, a limit enforced on the EVM host but not in pallet-ismp or on one consensus client but not its L2 twin, escrow or storage deposits stranded on an error path that still emits the event, or value carried across a runtime migration, decimals update or params change that was only proven safe on one side - yielding theft or permanent freezing of user funds, an unbacked mint, or a route that can never deliver messages again.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one Hyperbridge target.

    ```
    target_file format:
    "'File Name: modules/ismp/core/src/handlers/request.rs -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit questions for this exact Hyperbridge target:

    {target_file}

    Project focus:
    Hyperbridge is a permissionless cross-chain interoperability coprocessor. Focus only on what an ordinary user reaches: dispatching POST/GET requests and responses through EvmHost or pallet-ismp, relaying (anyone may relay, with no stake or whitelist) by calling HandlerV2.handleConsensus/handlePostRequests/handleGetResponses/handlePostRequestTimeouts/handleGetRequestTimeouts with self-supplied consensus and state proofs or submitting pallet_ismp handle_unsigned, bridging tokens through HyperFungibleToken and pallet-hyper-fungible-token, placing/filling/cancelling intent orders and bids, purchasing bandwidth, and claiming relayer fees and delivery rewards. Downstream of that: consensus client updates, state commitment storage, membership and non-membership proof verification, MMR accumulation, and app onAccept/onTimeout callbacks.

    Rules:
    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact symbols (Rust fn/struct/enum/trait impl, or Solidity function/modifier/struct/storage var) when possible.
    * Attacker is unprivileged only: anyone who funds an EOA or Hyperbridge account and submits transactions or extrinsics, deploys and calls their own ISMP module contract, dispatches requests and responses, relays any message or consensus update with proofs they construct, bridges tokens, or places bids and orders. They control only their own keys.
    * Attacker is NOT an admin, owner, host manager, governance origin, collator, validator, fisherman with privileged origin, node operator, prover or host owner, and holds no other user's key. Never assume a malicious peer, malicious node, malicious collator, p2p/gossip/sync attacker, network-level DoS, leaked key, compromised host, non-default config, or social engineering.
    * Out of scope, never ask about: p2p networking and peer handling, collator selection and block production, the tesseract relayer daemon and its config, RPC/runtime-api/offchain-index endpoints used only for indexing, CLI, logging, deployment and infra, dependency versions.
    * Ignore test files, mocks, benchmarks, weights, docs, generated files, and config-only findings.
    * Every question must describe a real transaction, extrinsic, dispatched request, relayed message with proof, token transfer, order or bid the attacker actually submits through a valid entrypoint. No generic unbounded-allocation, memory-growth, storage-growth or resource-exhaustion speculation; no "what if the input is huge" without a concrete submitted payload and a concrete broken invariant.
    * Generate 40 to 80 high-signal questions.
    * At least 70% must target theft or permanent freezing of user funds, an unbacked mint, delivery of a message that was never dispatched, acting on an app or account without its keys, a forged state commitment, or a route that can never deliver messages again.
    * Every question must be testable by a `cargo test -p <crate>` unit test, a pallet testsuite test, a `forge test` against the EVM contracts, or an ISMP end-to-end flow test.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Message authenticity: a request, response or timeout is acted on only when a verified consensus state and state proof bind it to a commitment actually dispatched by the named source module on the named source chain.
    * Exactly-once delivery: every commitment is delivered at most once, timed out at most once, and never both; commitments are collision-free across POST, GET, response and chain.
    * Value conservation: tokens minted on one chain are backed by tokens burned or escrowed on another, fees and rewards are paid once to the party that earned them, and no path strands or duplicates escrowed value.
    * Consensus soundness: a state commitment is stored only when the submitted proof meets the client's signature, threshold, finality and authority-set rules for the claimed height.
    * Liveness of valid users: no submitted message, proof or order can permanently stop a consensus client from advancing or an in-flight message from being delivered or refunded.

    Each question must include:
    1. target function/method;
    2. attacker action (a concrete transaction, extrinsic, dispatched request, relayed proof, token transfer, order or bid: fields, chain, calldata);
    3. preconditions (accounts, balance, deployed modules, tracked chains the attacker relies on);
    4. execution sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger EXECUTION_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: cargo test / pallet testsuite / forge test / ISMP end-to-end test PARAMETERS and assert MESSAGE_AUTHENTICITY, EXACTLY_ONCE_DELIVERY, VALUE_CONSERVATION, CONSENSUS_SOUNDNESS, or USER_LIVENESS.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused Hyperbridge exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: anyone who dispatches requests or responses, relays any message or consensus update with self-supplied proofs, deploys and calls their own ISMP module, bridges tokens, places orders or bids, or claims relayer fees. No admin, owner, host manager, governance origin, collator, validator, prover, node, host, or foreign-key access.
- Reject malicious-admin, malicious-governance, malicious-collator, malicious-peer, malicious-node, p2p/gossip/sync, network-DoS, leaked-key, host-level, and misconfiguration-only paths.
- Reject 51%-style, sybil and centralization claims, third-party oracle data simply being wrong with no manipulation path, and monitoring, CLI, logging, deployment, tesseract-daemon, dependency-only, and test/mock/bench/generated/config-only findings.
- Reject generic unbounded-allocation or storage-growth claims with no concrete submitted payload and no broken invariant.
- Focus on real chain impact: theft or permanent freezing of user funds, an unbacked mint or broken supply conservation, delivery of a message never dispatched on the source chain, a forged or unsound state commitment, acting on an app without authorization, or a route permanently unable to deliver messages.

## Validate
- Trace the exact reachable path from the attacker's transaction, extrinsic, dispatched request, relayed proof, token transfer or order into the affected function.
- Check whether consensus verification, challenge period and unstaking period, state-proof membership checks, request/response receipts and commitment maps, nonce and timeout checks, source-chain and source-module authorization, or existing error handling already stop it.
- Confirm the path is reachable on current mainnet (nexus) configuration and the deployed EvmHost/HandlerV2 wiring.
- Accept only concrete fund loss or freezing, unbacked mint, forged message delivery, unsound commitment, unauthorized app action, or a lasting inability to deliver messages.
- Require exact file/function support and a reproducible cargo test, pallet testsuite test, forge test, or ISMP end-to-end PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker payload, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact and severity: Critical (direct theft or permanent freezing of user funds, unbacked mint or supply inflation, delivery of a message never dispatched, forged state commitment, protocol insolvency) or High (a route or consensus client permanently unable to deliver messages, corruption of committed commitments, honest nodes diverging on Hyperbridge state)]

### Likelihood Explanation
[Preconditions, accounts and balance needed, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[cargo test / pallet testsuite / forge test / ISMP end-to-end test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for Hyperbridge.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production repo context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only analogs an unprivileged message dispatcher, relayer, token bridger, intent solver or bandwidth purchaser can reach: EvmHost and HandlerV2 dispatch and delivery, Message encoding and commitment hashing, consensus verification (BEEFY, SP1, sync-committee, GRANDPA, BSC, Tendermint, Pharos, L2 clients), state membership and non-membership proofs, pallet-ismp handle_unsigned and child-trie commitments, MMR accumulation, token bridge mint/burn, intents escrow and bids, or relayer fee and reward accounting.
- Reject malicious-admin, malicious-governance, malicious-collator, malicious-peer, malicious-node, p2p/sync, network-DoS, leaked-key, prover-only, monitoring, CLI, deployment, tesseract-daemon, mocked-only paths, dependency-only bugs, and no-impact analogs.
- Medium, High and Critical only; no low, or resource-only analogs.

## Validate
- Map the bug class to the strongest reachable Hyperbridge path from a single submitted transaction, extrinsic, dispatched request, relayed proof, token transfer or order.
- Prove root cause with exact file/function support.
- Accept only concrete theft or permanent freezing of funds, unbacked mint, forged message delivery, unsound state commitment, unauthorized app action, or a route unable to deliver messages.

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
    Generate a strict bounty-style validation prompt for Hyperbridge security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Focus on High and Critical; reject informational, best-practice, and resource-only reports.
- Reject malicious-admin, malicious-governance, malicious-collator, malicious-validator, malicious-peer, malicious-node, p2p/gossip/sync, network-level DoS, monitoring endpoints, CLI, logging, deployment and infra, tesseract-daemon, dependency-only, docs/style, generated-file, and test/mock/bench/weights/config-only issues.
- Reject if the exploit needs admin, owner, host-manager, governance, collator, validator, prover, node, host, database, or privileged origin access, another user's key, victim social engineering, a non-default config, or anything outside what an unprivileged user can put in a transaction, extrinsic, dispatched request, relayed proof, token transfer, order or bid.
- Reject 51%-style majority attacks, sybil and centralization claims, and third-party oracle data being wrong without a manipulation path.
- Reject if the bug was fixed, acknowledged, or publicly disclosed already, per the eligibility rules.
- A valid report must be triggerable by an unprivileged dispatcher, relayer, token bridger, solver or bidder, unless the claim proves escalation from that starting point.
- The final impact must map to an in-scope category: Critical - direct theft or permanent freezing of user or escrowed funds, unbacked mint or broken cross-chain supply conservation, delivery of a message never dispatched on the source chain, a forged or unsound state commitment, acting on an app or account without authorization, or protocol insolvency; High - a route or consensus client permanently unable to deliver messages, corruption of committed commitments or MMR leaves, or honest nodes diverging on Hyperbridge state.
- Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken message-authenticity, exactly-once-delivery, value-conservation, consensus-soundness, or user-liveness invariant.
3. Reachable exploit path: preconditions (attacker accounts, balance, deployed modules, tracked chains) -> submitted transaction, extrinsic, dispatched request, relayed proof, token transfer or order -> trigger -> bad result.
4. Existing consensus verification, challenge and unstaking periods, state-proof checks, receipts and commitment maps, nonce and timeout checks, source-chain and source-module authorization, and error handling reviewed and shown insufficient.
5. Concrete in-scope High/Critical impact with realistic likelihood.
6. Reproducible proof path: cargo test unit PoC, pallet testsuite test, forge test, or exact steps in an ISMP end-to-end flow.
7. No obvious rejection reason from SECURITY.md, known issues, privilege assumptions, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can an ordinary user trigger this by dispatching a request, relaying a message or consensus update with proofs they build, bridging tokens, or placing an order or bid, without admin, governance, collator, prover, host, or foreign-key access?
- Does the code actually behave as claimed on current mainnet (nexus) configuration and the deployed host wiring?
- Is the impact caused by this code, not by a privileged actor, a peer, or a dependency?
- Is the fund loss, unbacked mint, forged delivery, or halt concrete rather than hypothetical?
- Would a bridge-protocol triager accept the proof-of-concept?
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
[Concrete in-scope impact, severity rationale, and Hyperbridge bounty category]

## Likelihood Explanation
[Attacker capability, accounts and balance required, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or cargo test / pallet testsuite / forge test / ISMP end-to-end test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt
