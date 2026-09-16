### Title
Treasury-Funded Relayer Reward Payouts Have No Debt-Tracking When the Treasury Account Is Insolvent - ([File: modules/pallets/relayer/src/lib.rs])

### Summary
Hyperbridge pays relayers a governance-configured reward from a shared treasury `PalletId` account for two permissionless, cryptographically-proven claims: `claim_outbound_consensus_delivery_reward` (consensus rotation delivery) and the analogous outbound-request delivery claim described in `docs/outbound-request-incentivization.md` (`process_outbound_request_delivery_claim`). Both pay `reward` straight from the treasury account to the claiming relayer once a state proof of delivery validates. Like the original C4 finding, there is no accounting for what happens once the payer (treasury) can no longer cover what it legitimately owes — the transfer simply fails, and no IOU/IOU-repayment or top-up mechanism exists in the codebase to make the relayer whole later.

### Finding Description
`modules/pallets/relayer/src/lib.rs` defines the relevant errors: [1](#0-0) [2](#0-1) 

Both `OutboundRewardTransferFailed` and `OutboundRequestRewardTransferFailed` are explicitly documented as occurring "typically because the treasury balance is below the configured reward." The reward transfer is the terminal step of an otherwise fully permissionless, cryptographic verification pipeline (`docs/outbound-request-incentivization.md`, steps 1–12): any relayer who proves delivery of a hyperbridge-originated request is entitled to `OutboundRequestDeliveryReward[module_id]`, and payment happens "at claim time against a destination state proof" directly out of the treasury account — there is no escrow specifically reserved per outstanding reward, no cap tied to actual treasury inflows, and no queued/IOU state for a claim that a relayer has legitimately earned but that the treasury currently cannot pay: [3](#0-2) 

This mirrors the insurance protocol's flaw precisely: like `PoolTemplate.resume()` calling `vault.transferDebt()` once the Index/CDS compensation layers are exhausted with no mechanism to guarantee the accrued debt is ever repaid, Hyperbridge's reward path has no fallback when the treasury payer is exhausted relative to outstanding, provably-earned relayer claims. The relayer's claim is not persisted as a payable debt for later settlement — a failed transfer simply aborts the extrinsic (state changes revert under the pallet's transactional call semantics), so the relayer must resubmit the exact same proof indefinitely until governance manually refills the treasury, with no on-chain acknowledgement, interest, or backstop token minting analogous to the "mint INSURE" mitigation the insurance protocol eventually adopted.

### Impact Explanation
If treasury outflows (paid to any relayer proving delivery of system messages: host-parameter propagation, host-executive updates, intents-coprocessor responses, token-governor messages, relayer withdrawal requests, and consensus rotation deliveries) ever exceed treasury inflows — which is entirely plausible since claims are permissionless and rewards are a fixed governance-set amount per module/rotation, independent of treasury balance — every relayer with a legitimately proven, unpaid claim is permanently frozen out of their reward until governance notices and manually replenishes the account. Because there's no debt ledger, relayers cannot be prioritized, refunded pro-rata, or otherwise compensated for the shortfall period; the incentive to relay Hyperbridge's own system messages (some of which, like consensus rotations, are security-critical) can silently collapse, degrading delivery of these system messages ("a route unable to deliver messages").

### Likelihood Explanation
The claim path is unsigned/permissionless and triggered by ordinary relayer activity — no privileged actor is required to reach the insolvency condition, only sustained normal operation faster than treasury top-ups. This matches the "extreme edge case" framing of the original report but is reachable purely by the volume of legitimate, cryptographically-proven relayer claims against a treasury whose replenishment is governance-paced and asynchronous.

### Recommendation
Introduce an on-chain debt ledger for reward claims that fail due to insufficient treasury balance (mirroring the "system debt" storage pattern the original report's sponsor ultimately adopted): mark the claim as verified-but-unpaid, and either (a) automatically retry/settle once the treasury balance recovers, or (b) allow permissionless "repay debt" settlement transactions to top off outstanding relayer IOUs, so that a relayer's proven, legitimate claim is never irrecoverably dropped by a point-in-time treasury balance check.

### Proof of Concept
1. Governance sets a non-zero `OutboundRequestDeliveryReward[module_id]` (or `OutboundConsensusDeliveryReward[destination]`), and the treasury account holds `B` tokens.
2. Multiple relayers submit proofs of distinct, legitimate deliveries whose cumulative reward exceeds `B`.
3. The first several claims succeed, depleting the treasury below `B`.
4. A subsequent, fully valid delivery-proof claim reaches step 11 in `process_outbound_request_delivery_claim` and the transfer fails, returning `OutboundRequestRewardTransferFailed`/`OutboundRewardTransferFailed` (analogous behavior demonstrated for `IHostManager.withdraw` insufficient-balance reverts in `evm/tests/rust/src/tests/host_manager.rs`): [4](#0-3) 
5. No storage records that this relayer is still owed the reward; the relayer must guess when to resubmit the identical proof, and nothing on-chain tracks or repays the shortfall — matching the acknowledged-but-unmitigated "system debt" root cause from the source report.

### Citations

**File:** modules/pallets/relayer/src/lib.rs (L229-234)
```rust
		/// Treasury → relayer transfer failed (typically because the
		/// treasury balance is below the configured reward).
		OutboundRewardTransferFailed,
		/// No reward is configured for the destination
		/// (`OutboundConsensusDeliveryReward` is `0`).
		OutboundNoRewardConfigured,
```

**File:** modules/pallets/relayer/src/lib.rs (L264-266)
```rust
		/// Treasury → relayer transfer failed (typically because the treasury
		/// balance is below the configured reward).
		OutboundRequestRewardTransferFailed,
```

**File:** docs/outbound-request-incentivization.md (L112-142)
```markdown
### Verification pipeline

`process_outbound_request_delivery_claim` runs these checks in order. Ordering is deliberate: every cheap rejection happens before the state-proof verification, so non-allowlisted claims and replays are dropped without ever touching the trie verifier.

1. **Hash the request.** `commitment = hash_request::<IsmpHost>(&Request::Post(request))`. The relayer never gets to pick the commitment.

2. **Source check.** `request.source` must equal `IsmpHost::host_state_machine()`. Rejects forged claims for requests that didn't originate on this hyperbridge instance.

3. **Local presence check.** `pallet_ismp::child_trie::RequestCommitments::get(commitment).is_some()`. Defence in depth on top of the source check: the dispatcher already enforces source on insert, so anything missing from the trie was never dispatched here.

4. **Idempotency.** Reject if `OutboundRequestsClaimed[commitment]` is set.

5. **Module-id bound.** `BoundedVec::<u8, ModuleIdBound>::try_from(request.from.clone())`. Anything longer than 64 bytes is treated as not on the allowlist.

6. **Allowlist lookup.** `reward = OutboundRequestDeliveryReward::<T>::get(module_id)`. If zero, reject. This is the only place the allowlist is enforced; governance enables a module by setting a non-zero reward.

7. **State-machine match.** `state_proof.height.id.state_id == request.dest`. Defends against a relayer building a proof against a different chain than the request was sent to.

8. **Destination type and receipt key.** Use the `Pallet::request_receipt_key` helper (defined alongside the claim in `outbound_request.rs`):
   - EVM destinations: 32-byte slot hash `derive_unhashed_map_key(commitment, REQUEST_RECEIPTS_SLOT)`, the same key the EVM state machine's `receipts_state_trie_key` produces.
   - Substrate destinations: `pallet_ismp::child_trie::RequestReceipts::<T>::storage_key(commitment)`, identical to the substrate state machine's receipt key.

   A destination that is neither EVM nor substrate is rejected with `OutboundRequestUnsupportedDestination`.

9. **State proof verification.** Resolve the destination client with `ismp::handlers::validate_state_machine(&host, height)`, then `verify_withdrawal_proof(state_machine, &state_proof, vec![key])` against hyperbridge's stored state commitment for the destination. A verification failure maps to `OutboundDestinationStateNotKnown` (no commitment at that height), and a missing or null slot value maps to `OutboundDeliveryNotProven`.

10. **Signature attribution.** Recover the signer from `signature.verify(&outbound_request_delivery_message(commitment, destination, payee), None)` and check it matches the address proven in the receipt slot. For EVM, both are 20-byte addresses; for substrate, the bytes from the receipt must equal `signature.signer()`. Mismatch → `OutboundRequestSignerMismatch`.

11. **Payout.** Transfer `reward` from the treasury PalletId account to `payee`.

12. **Persist and emit.** Insert `OutboundRequestsClaimed[commitment] = ()`. Deposit `OutboundRequestDeliveryRewarded { commitment, state_machine: destination, module_id, relayer: payee, amount: reward }`.
```

**File:** evm/tests/rust/src/tests/host_manager.rs (L152-181)
```rust
#[test]
fn test_host_manager_insufficient_balance() {
	let mut env = TestEnv::new();
	let manager = host_manager_of(&mut env);

	// Host has no fee tokens; withdraw attempt should fail on SafeERC20 transfer
	let params = WithdrawalParams {
		beneficiary_address: H160::random().as_bytes().to_vec(),
		amount: SubstrateU256::from(500_000_000_000_000_000_000u128),
		token: H160::from_slice(env.fee_token.as_slice()),
	};

	let post = router::PostRequest {
		source: StateMachine::Kusama(2000),
		dest: StateMachine::Evm(1),
		nonce: 0,
		from: env.sender.as_slice().to_vec(),
		to: vec![],
		timeout_timestamp: 100,
		body: params.abi_encode().expect("20-byte beneficiary"),
	};
	let evm_request: EvmPostRequest = post.into();

	let host_addr = env.host;
	let calldata = onaccept_calldata(evm_request, env.sender);
	let err = env
		.call_as_may_revert(host_addr, manager, calldata)
		.expect_err("expected revert");
	assert!(!err.is_empty(), "expected non-empty revert data");
}
```
