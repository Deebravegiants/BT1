## Analysis

The M-12 pattern — computing a payout using a *live*, mutable configuration value fetched at claim/settlement time instead of a value that was fixed/snapshotted at the time the entitlement was created — has a direct analog in Hyperbridge's outbound-request delivery reward pipeline.

`pallet_ismp_relayer::process_outbound_request_delivery_claim` re-reads `OutboundRequestDeliveryReward[module_id]` at claim time to determine both eligibility and payout amount: [1](#0-0) 

This value is stored per `module_id`, not per dispatched request/commitment, and is freely mutable via the privileged `set_outbound_request_delivery_reward` extrinsic: [2](#0-1) 

A hyperbridge-originated `PostRequest` is dispatched and its commitment recorded in `RequestCommitments` while a given reward is active for its `from` module id. The relayer then has to deliver it to the destination and later submit `claim_outbound_request_delivery_reward` to get paid — an unbounded window during which governance can legitimately re-tune `OutboundRequestDeliveryReward` for that module (e.g., lowering incentive economics, or fully removing a module from the allowlist by zeroing its reward). Because the claim path reads the reward map fresh rather than the value in effect when the request was dispatched, any request dispatched under the old reward that is still unclaimed when the reward is changed is settled against the *new* value — and if the module is deallowlisted (reward set to `0`), the check at line 149 rejects the claim outright with `OutboundRequestNoRewardConfigured`, permanently and irrecoverably losing the entitlement for a relayer that already delivered the message and cannot re-claim it since `OutboundRequestsClaimed` idempotency would also block a second attempt once/if the reward were restored differently, and there is no per-commitment stored reward to fall back on.

This mirrors the root cause of M-12 precisely: `pendingRewards` in `WAuraPools`/`WConvexPools` recomputed the reward-token list live from the underlying Aura/Convex contracts rather than storing it at deposit time, so removing a reward token from the pool orphaned already-accrued entitlements. Here, the reward *rate/eligibility* for an already-dispatched, already-committed request is likewise re-derived live from mutable storage rather than snapshotted at dispatch time into the request's commitment/metadata.

### Title
Outbound request delivery reward is read from live, mutable `OutboundRequestDeliveryReward` storage instead of being snapshotted at dispatch time, permanently losing relayer entitlements when the module's reward is changed or zeroed - (File: `modules/pallets/relayer/src/outbound_request.rs`)

### Summary
`process_outbound_request_delivery_claim` looks up the payout reward for a delivered hyperbridge-originated request by reading the *current* value of `OutboundRequestDeliveryReward[module_id]` at claim time, rather than the value that was in effect when the request was dispatched and its commitment recorded.

### Finding Description
When a hyperbridge-originated `PostRequest` is dispatched from a module, its commitment is stored in `pallet_ismp::child_trie::RequestCommitments` [3](#0-2) . Relayers subsequently deliver the request off-chain to the destination and later call `claim_outbound_request_delivery_reward` to prove delivery and get paid. At claim time, the pallet determines both the eligibility and payout amount by reading `OutboundRequestDeliveryReward::<T>::get(&module_id)` [4](#0-3) , which is a live, governance-mutable `StorageMap` keyed only by `module_id`, updated via `set_outbound_request_delivery_reward` [2](#0-1) .

There is no per-request/per-commitment snapshot of the reward amount that was active at dispatch time. Consequently:
- If governance lowers or zeroes a module's reward (e.g. to retire that module from the incentive allowlist, or rebalance treasury economics) between the time a request is dispatched and the time the delivering relayer submits its claim, any already-dispatched-but-unclaimed request from that module is settled at the new (possibly zero) rate.
- A reward of `0` causes `ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundRequestNoRewardConfigured)` to reject the claim entirely [4](#0-3) . Since `OutboundRequestsClaimed` records commitments only on a successful payout [5](#0-4) , the claim can be retried indefinitely, but it will never succeed while the reward remains zero — the relayer's earned entitlement for that specific, already-delivered request is permanently unpayable, exactly as in M-12 where removed reward tokens became permanently unclaimable because they weren't pinned per-tokenID.

### Impact Explanation
A relayer that has already spent gas/resources proving delivery of a hyperbridge-originated request is entitled to a reward fixed by the protocol's incentive design at the time the message was dispatched. Because the payout is computed from live storage instead of a value bound to the commitment, a legitimate governance action to update or retire a module's reward rate silently and permanently strips already-earned entitlements for requests dispatched before the change but claimed after it. This is a loss-of-funds bug in the reward accounting path affecting the relayer incentive mechanism that Hyperbridge relies on for message delivery economics.

### Likelihood Explanation
`set_outbound_request_delivery_reward` is an expected, routine operational call for governance (adjusting incentive allowlists/economics), not an attack — the same operational category as the removal of an "extra reward token" in the original Aura/Convex report. Any relayer that delivers a request close to (but after) such a reward update is affected, and the claim window between dispatch and claim submission is unbounded, making the race condition realistically triggerable during normal operations.

### Recommendation
Snapshot the reward amount (and/or allowlist eligibility) into the request's commitment metadata (e.g. alongside `RequestCommitments`/`RequestMetadata`) at dispatch time, and have `process_outbound_request_delivery_claim` pay out using that stored value rather than re-reading the live `OutboundRequestDeliveryReward` map. If backward-compatible storage changes are constrained, at minimum record a historical reward-rate log keyed by an effective block range so claims can resolve the rate that was active when the request was dispatched.

### Proof of Concept
1. Governance calls `set_outbound_request_delivery_reward(module_id, REWARD)`, allowlisting `module_id` with a non-zero reward.
2. A module dispatches a `PostRequest` with `from = module_id`; its commitment is recorded in `RequestCommitments`.
3. A relayer delivers the request to the destination (writing `RequestReceipts[commitment]`), but has not yet submitted the on-chain claim.
4. Before the relayer claims, governance calls `set_outbound_request_delivery_reward(module_id, 0)` to retire the module from the allowlist (a legitimate, routine action, e.g. superseding it with a new module id).
5. The relayer submits `claim_outbound_request_delivery_reward` for the already-delivered request; `OutboundRequestDeliveryReward::<T>::get(&module_id)` now returns `0`, and the `ensure!` at [4](#0-3)  rejects the claim with `OutboundRequestNoRewardConfigured` — permanently, since the reward will never be restored to that state for that module. The relayer's entitled reward for a request they already correctly delivered is lost forever.

### Citations

**File:** modules/pallets/relayer/src/outbound_request.rs (L133-136)
```rust
		ensure!(
			RequestCommitments::<T>::get(commitment).is_some(),
			Error::<T>::OutboundRequestNotKnown,
		);
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L143-149)
```rust
		let module_id: BoundedVec<u8, ModuleIdBound> = request
			.from
			.clone()
			.try_into()
			.map_err(|_| Error::<T>::OutboundRequestModuleIdTooLong)?;
		let reward = OutboundRequestDeliveryReward::<T>::get(&module_id);
		ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundRequestNoRewardConfigured);
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L186-186)
```rust
		OutboundRequestsClaimed::<T>::insert(commitment, ());
```

**File:** docs/outbound-request-incentivization.md (L96-109)
```markdown
#[pallet::call_index(6)]
pub fn set_outbound_request_delivery_reward(
    origin: OriginFor<T>,
    module_id: BoundedVec<u8, ModuleIdBound>,
    amount: BalanceOf<T>,
) -> DispatchResult {
    T::RelayerOrigin::ensure_origin(origin)?;
    OutboundRequestDeliveryReward::<T>::insert(&module_id, amount);
    Self::deposit_event(Event::OutboundRequestDeliveryRewardUpdated {
        module_id,
        new_reward: amount,
    });
    Ok(())
}
```
