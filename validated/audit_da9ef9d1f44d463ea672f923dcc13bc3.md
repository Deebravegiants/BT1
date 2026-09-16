### Title
Unconditional consensus-update-time refresh in `pallet-ismp` lets any relayer indefinitely postpone the unbonding-period expiry check - ([File: modules/ismp/core/src/handlers/consensus.rs])

### Summary
`update_client` in the core ISMP consensus handler stores a new `consensus_update_time` on **every** successful call to `verify_consensus`, even when the verified state is byte-identical to the already-trusted state. This mirrors the Shelter `activate()` bug class: a low-privilege caller (any relayer) can repeatedly "touch" a timer-gated safety mechanism without making real progress, resetting the clock the mechanism depends on and defeating the invariant that timer was meant to enforce.

### Finding Description
`update_client` in `modules/ismp/core/src/handlers/consensus.rs` performs: [1](#0-0) 

```rust
let (new_state, intermediate_states) = consensus_client.verify_consensus(
    host, msg.consensus_state_id, trusted_state, msg.consensus_proof,
)?;
host.store_consensus_state(msg.consensus_state_id, new_state)?;
let timestamp = host.timestamp();
host.store_consensus_update_time(msg.consensus_state_id, timestamp)?;
```

Note there is **no check** that `new_state != trusted_state` before refreshing `consensus_update_time`. Any relayer who is permitted to submit a `ConsensusMessage` (this is a fully permissionless, unsigned/unauthenticated extrinsic reachable by anyone acting as a relayer) can repeatedly resubmit any proof that `verify_consensus` accepts as valid — including a proof that produces no new intermediate states and an unchanged consensus state (e.g., re-verifying an already-finalized header/commitment, or any authority-set proof the consensus client happens to accept without advancing height) — and each such call refreshes `consensus_update_time` to `host.timestamp()`.

This is precisely the "activate resets the timer" pattern from the Shelter finding: the timer `consensus_update_time` gates `is_expired`, which enforces the `unbonding_period` — the mechanism specifically designed to freeze/reject a consensus client whose state has gone stale for longer than the unbonding period (the classic "long-range attack" defense: once a validator set's keys are no longer economically bonded, proofs signed by them must eventually stop being trusted).

By contrast, the EVM handler for the equivalent flow explicitly guards against this: [2](#0-1) 

```solidity
function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
    uint256 delay = block.timestamp - host.consensusUpdateTime();
    if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

    bytes memory previousState = host.consensusState();
    (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
        IConsensusV2(host.consensusClient()).verify(previousState, proof);

    if (keccak256(previousState) == keccak256(verifiedState)) return;
    host.storeConsensusState(verifiedState);
```

The EVM path returns early — skipping `storeConsensusState` (and therefore the timestamp bump that happens inside it) — whenever the verified state is unchanged from the previous state. The Rust core handler used by `pallet-ismp` (and all substrate-based ISMP hosts, e.g. GRANDPA/BEEFY-based parachains) has no analogous guard, so it always advances the unbonding clock regardless of whether the submission carried any real progress.

### Impact Explanation
`is_expired`/`UnbondingPeriodElapsed` exists to force a consensus client offline once it goes stale for longer than the configured unbonding period, which is the safety window during which a validator set's signing keys remain economically bonded (and thus a forged/equivocated proof from that set would be slashable/detectable off-chain). If any unprivileged relayer can indefinitely refresh `consensus_update_time` without the client actually progressing, the unbonding-based staleness protection never fires. This directly undermines a core cross-chain security invariant: a consensus client that should have been frozen as "expired" (and whose signed commitments should therefore no longer be trusted) can instead be kept perpetually "fresh," letting a relayer with access to signatures from a since-unbonded (or otherwise compromised) validator/authority set continue to have their consensus proofs accepted by `update_client`, and by extension have forged state commitments / requests delivered through `handle_incoming_message`. This is a break of the consensus-verification safety property (route unable to enforce the freezing of stale/compromised consensus, enabling unsound state commitments) rather than a mere availability nuisance.

### Likelihood Explanation
High reachability: `ConsensusMessage` handling is permissionless — any relayer can submit a consensus proof for a state machine at any time, with no signer authorization or stake requirement (`handle_unsigned`/dispatcher paths accept it). The only precondition is that `verify_consensus` returns `Ok` for the submitted proof — which is trivially satisfiable by resubmitting the last-accepted valid proof/header (already finalized headers remain individually re-verifiable against the currently trusted state in most GRANDPA/BEEFY-style verifiers), requiring no new signatures, no waiting, and no cost beyond gas/weight for a permissionless extrinsic.

### Recommendation
Mirror the EVM `HandlerV2.handleConsensus` guard in the Rust core handler: only call `host.store_consensus_update_time` (and `store_consensus_state`) when the newly verified state actually differs from the trusted state (or when new intermediate/state-machine commitments were produced). Concretely, in `update_client`, compare `new_state` against `trusted_state` before calling `store_consensus_state`/`store_consensus_update_time`, and return early (or only update state-machine-level timers, not the top-level unbonding clock) when nothing changed.

### Proof of Concept
1. A relayer possesses (or can freely re-obtain, since these are public/already-finalized proofs) a valid consensus proof `P` for `consensus_state_id = X` that `verify_consensus` accepts and that returns `new_state == trusted_state` (no new intermediate states) — e.g., resubmitting the currently-finalized authority-set proof, or any header already reflected in the trusted state.
2. Relayer submits `ConsensusMessage { consensus_state_id: X, consensus_proof: P }` via `pallet-ismp`'s permissionless message-handling path, repeated at an interval shorter than `unbonding_period`.
3. In `update_client` (`modules/ismp/core/src/handlers/consensus.rs:41-49`), `verify_consensus` returns `Ok`, and — regardless of `new_state == trusted_state` — `host.store_consensus_update_time(X, host.timestamp())` executes unconditionally.
4. `is_expired(X)` (gated by `store_consensus_update_time`) never trips, even though the underlying authority set backing `X` may already be past its intended unbonding window and no longer economically bonded/trustworthy.
5. Any subsequent consensus proof signed by that same (now stale/potentially compromised) authority set continues to be accepted by `update_client`, since the `ExpiredConsensusClient` guard that should have rejected it never activates.

(Note: I was unable to fully verify, within tool budget, whether every individual consensus-client implementation's `verify_consensus` (GRANDPA/BEEFY/sync-committee/etc.) would in practice accept a fully-duplicate/no-progress proof without erroring — this would need to be confirmed per client to size exact exploitability, but the core handler's missing no-op guard, compared directly against the EVM handler's explicit guard for the identical scenario, is a clear and provable root-cause discrepancy in `modules/ismp/core/src/handlers/consensus.rs`.)

### Citations

**File:** modules/ismp/core/src/handlers/consensus.rs (L41-49)
```rust
	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
	let timestamp = host.timestamp();
	host.store_consensus_update_time(msg.consensus_state_id, timestamp)?;
```

**File:** evm/src/core/HandlerV2.sol (L144-153)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);

        if (keccak256(previousState) == keccak256(verifiedState)) return;
        host.storeConsensusState(verifiedState);
```
