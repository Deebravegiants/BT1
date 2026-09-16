I have enough context now. This maps cleanly to the bug class: a permissionless, first-write-wins address-attribution slot that any unprivileged caller can race to claim, permanently locking out the legitimate party from the associated reward.

### Title
First-submitter epoch attribution in `EvmHost.recordEpoch` lets an attacker front-run and permanently steal a competing relayer's `OutboundConsensusDeliveryReward` - (File: evm/src/core/EvmHost.sol / modules/pallets/relayer/src/outbound_consensus.rs)

### Summary
`HandlerV2.handleConsensus` credits whichever address's transaction happens to land first for a given authority-set epoch by calling `EvmHost.recordEpoch(epoch, msg.sender)`, permanently and irrevocably writing `_epochs[epoch]`. This is the same "assignment front-running" bug class as the reported delegateKey race: any address can call `handleConsensus` with a valid-but-otherwise-worthless consensus proof to claim the epoch slot for itself, permanently denying the legitimate/faster relayer any path to correct or reclaim that attribution, and diverting the on-chain-attributed `OutboundConsensusDeliveryReward` on Hyperbridge to the front-runner.

### Finding Description
`HandlerV2.handleConsensus` verifies a consensus proof and, when a rotation occurs, calls `host.recordEpoch(epoch, _msgSender())`: [1](#0-0) 

`EvmHost.recordEpoch` is a one-shot, unprivileged-caller-driven write: the *first* transaction that lands a given `authoritySetId` on chain wins the slot permanently, and every subsequent call for that (or an older) epoch is silently ignored (`if (authoritySetId <= _currentEpoch) return;`): [2](#0-1) 

`handleConsensus` itself is callable by anyone with any valid consensus proof — there is no restriction tying the caller to a particular relayer identity, and the proof only needs to be *valid*, not "the caller's own work": [3](#0-2) 

This is exactly the same class of bug as the reported delegateKey front-running: a shared, unprivileged-writable "claim slot" (`_epochs[epoch]` here, `memberAddressByDelegateKey`/`delegateKey` there) is assigned on a first-come-first-served basis with no way for the rightful party to contest, cancel, or reassign it after the fact. Since consensus proofs for a given epoch transition are public/derivable by anyone watching the relay chain (there is no exclusivity or staking requirement to submit them), any address can front-run the legitimate relayer's `handleConsensus` transaction — by copying the proof bytes from the mempool or independently deriving them — and land its own transaction first, permanently capturing `_epochs[epoch]` for itself.

The on-chain-verifiable `OutboundConsensusDeliveryReward` claim path on Hyperbridge explicitly keys off this same "first submitter wins" attribution and treats it as authoritative and unforgeable: [4](#0-3) [5](#0-4) 

Because `process_outbound_consensus_delivery_claim` only pays whoever's signature recovers to the address recorded in `_epochs[set_id]`, and that recording is permanent and unprivileged, an attacker who front-runs `handleConsensus` becomes the *sole* eligible claimant for that epoch's reward — the legitimate relayer who actually did the work of watching the relay chain and preparing/broadcasting the proof gets nothing and has no recourse, mirroring the reported bug's "only way to free the delegate is [an action that is itself irreversible]" pattern.

### Impact Explanation
This is a fund-diversion vulnerability against the relayer incentive mechanism, not merely a griefing/DoS: the `OutboundConsensusDeliveryReward` (paid from the Hyperbridge treasury) is permanently redirected from the relayer that should be economically incentivized to deliver consensus proofs promptly, to any opportunistic address willing to copy and resubmit a public proof with slightly higher gas/priority. Over time this can be automated (MEV-style) to systematically capture the reward pool for every rotation without contributing any of the actual relayer infrastructure Hyperbridge is trying to incentivize, degrading network security (fewer relayers with a real economic incentive to submit rotations promptly) and directly costing the protocol treasury.

### Likelihood Explanation
High. `handleConsensus` is a fully public, unauthenticated entry point (`external`, gated only by `notFrozen(host)`); consensus proofs are broadcast data with no confidentiality, so any address can observe a pending/likely proof and race to submit it first, including via standard mempool front-running (higher gas price) or by independently constructing the same proof from public relay-chain data. No special access, staking, or privileged role is required.

### Recommendation
- Do not attribute the epoch-delivery reward purely to `msg.sender` of the first successful `handleConsensus` call. Instead, tie attribution to a signed/committed claim (similar to the `OutboundRequestDeliveryClaim`/`OutboundConsensusDeliveryClaim` payee mechanism already used elsewhere) so the entity that actually produced/holds the proof-signing key benefits, not merely whoever's transaction is mined first.
- Consider a commit-reveal or minimum-bond scheme for `handleConsensus` submissions so front-running a public proof is not costless.
- At minimum, allow governance/relayer-identity-bound submission (e.g., require the caller to be a registered relayer, or split rewards among multiple submitters within a short window) so a single opportunistic front-runner cannot permanently and exclusively capture the reward for an epoch.

### Proof of Concept
1. Relayer R observes on the relay chain that a new authority-set rotation (epoch `E`) has finalized and begins preparing/broadcasting a `handleConsensus(host, proof)` transaction to the destination `EvmHost`.
2. Attacker A monitors the mempool (or independently derives the same publicly-verifiable consensus proof) and submits an identical/equivalent `handleConsensus(host, proof)` call with a higher gas price.
3. A's transaction is mined first; `HandlerV2.handleConsensus` (evm/src/core/HandlerV2.sol:144-174) calls `host.recordEpoch(E, A)`, which permanently sets `_epochs[E] = A` (evm/src/core/EvmHost.sol:676-681) since `E > _currentEpoch`.
4. R's transaction, mined afterward, hits `if (authoritySetId <= _currentEpoch) return;` in `recordEpoch` and is silently a no-op — R's proof was correct and delivered value, but nothing is recorded for R.
5. A later submits `claim_outbound_consensus_delivery_reward` on Hyperbridge with a state proof of `EvmHost._epochs[E] == A` and a signature recovering to A (modules/pallets/relayer/src/outbound_consensus.rs:113-198); the pallet pays A the full `OutboundConsensusDeliveryReward` from the treasury. R has no way to reclaim or contest the epoch-`E` attribution.

### Citations

**File:** evm/src/core/HandlerV2.sol (L144-174)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);

        if (keccak256(previousState) == keccak256(verifiedState)) return;
        host.storeConsensusState(verifiedState);

        uint256 intermediatesLen = intermediates.length;
        for (uint256 i = 0; i < intermediatesLen; i++) {
            IntermediateState memory intermediate = intermediates[i];
            uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
            if (latestHeight != 0 && intermediate.height > latestHeight) {
                StateMachineHeight memory stateMachineHeight =
                    StateMachineHeight({stateMachineId: intermediate.stateMachineId, height: intermediate.height});
                host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
            }
        }

        // `nextAuthoritySetId` identifies the upcoming set; the relayer that delivered the proof
        // is credited as the relayer for the just-ended epoch (`nextAuthoritySetId - 1`).
        // If `nextAuthoritySetId == 0` no rotation has occurred, so there is nothing to record.
        if (nextAuthoritySetId == 0) return;
        uint256 epoch = nextAuthoritySetId - 1;
        if (epoch > host.currentEpoch()) {
            host.recordEpoch(epoch, _msgSender());
        }
    }
```

**File:** evm/src/core/EvmHost.sol (L670-681)
```text
    /**
     * @dev Record the relayer that first submitted a consensus proof for a new authority set epoch.
     * Only callable by the configured handler. Stale or duplicate epoch IDs are ignored.
     * @param authoritySetId the new authority set / epoch ID
     * @param relayer the relayer that delivered the consensus proof
     */
    function recordEpoch(uint256 authoritySetId, address relayer) external restrict(_hostParams.handler) {
        if (authoritySetId <= _currentEpoch) return;
        _currentEpoch = authoritySetId;
        _epochs[authoritySetId] = relayer;
        emit NewEpoch({authoritySetId: authoritySetId, relayer: relayer});
    }
```

**File:** modules/pallets/relayer/src/outbound_consensus.rs (L52-72)
```rust
/// Claim payload for [`Pallet::claim_outbound_consensus_delivery_reward`].
///
/// A relayer who delivered a mandatory (authority-set rotation) consensus
/// proof to an EVM destination uses this to collect the per-chain
/// `OutboundConsensusDeliveryReward`. The on-chain attribution is in the
/// destination's `EvmHost._epochs[set_id]` slot — `HandlerV2.handleConsensus`
/// forwards to `EvmHost.recordEpoch(set_id, msg.sender)` the first time a
/// consensus proof brings the new set id on chain. Verifying the relayer:
///
/// 1. `(destination, set_id)` has not already been claimed.
/// 2. State proof against Hyperbridge's stored commitment for `(destination, height)` yields an
///    `address` at the slot `keccak256(set_id || EVM_HOST_EPOCHS_SLOT)` of the destination's
///    `EvmHost` contract.
/// 3. The `signature` (`Signature::Evm`) recovers exactly that `address`, signing the
///    [`outbound_consensus_delivery_message`] payload over `(set_id, destination, payee)`.
///
/// Replay protection comes from the on-chain `(destination, set_id)`
/// idempotency tag in [`crate::pallet::OutboundConsensusRotationsClaimed`], not
/// from a per-relayer nonce — once a `(destination, set_id)` has been
/// claimed it cannot be claimed again, so a captured signature has no
/// way to be reused.
```

**File:** modules/pallets/relayer/src/outbound_consensus.rs (L164-172)
```rust
		let evm_address = Self::decode_epochs_slot_address(destination, &raw)
			.ok_or(Error::<T>::OutboundDeliveryNotProven)?;

		// Replay protection comes from the `OutboundConsensusRotationsClaimed`
		let msg = outbound_consensus_delivery_message(set_id, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		let recovered_address = Address::try_from(recovered.as_slice())
			.map_err(|_| Error::<T>::OutboundSignerMismatch)?;
		ensure!(recovered_address == evm_address, Error::<T>::OutboundSignerMismatch);
```
