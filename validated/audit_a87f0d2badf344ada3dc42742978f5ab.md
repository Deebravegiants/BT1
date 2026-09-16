## Finding

### Title
No incentive to relay hyperbridge-originated system requests (zero-fee dispatch) can permanently stall critical protocol messages and freeze relayer funds - (File: `modules/pallets/host-executive/src/lib.rs`, `modules/pallets/relayer/src/withdrawal.rs`, `modules/pallets/intents-coprocessor/src/lib.rs`, `modules/pallets/token-governor/src/impls.rs`)

### Summary
Just as DYAD's `liquidate()` only pays liquidators a small share of collateral, making sub-$150–200 positions unprofitable to liquidate and letting bad debt accumulate, several hyperbridge-originated ISMP requests are dispatched with **zero fee and zero payer**, giving relayers no economic reason to deliver them. Delivery of these messages depends entirely on altruism, and the compensating mechanism (`OutboundRequestDeliveryReward`) defaults to zero per module and must be explicitly set by governance — the exact same "team must self-liquidate/self-relay" acknowledgment pattern as the DYAD report.

### Finding Description
`pallet-ismp`'s `IsmpDispatcher::dispatch_request` only escrows a fee when `fee.fee != Zero::zero()` [1](#0-0) . Several system pallets that originate requests on Hyperbridge itself call this dispatcher with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }`:

- `pallet-host-executive`'s `update_host_params`, which propagates critical host-parameter changes (including manager rotation) to destination EVM hosts [2](#0-1) .
- The relayer pallet's own fee-withdrawal request path in `modules/pallets/relayer/src/withdrawal.rs`, which disburses a relayer's *own accumulated fees* to a beneficiary via an outbound POST [3](#0-2) .
- `pallet-intents-coprocessor` and `pallet-token-governor`, per the same zero-fee pattern documented in `docs/outbound-request-incentivization.md` [4](#0-3) .

The project's own design doc explicitly states the root cause: *"Zero fee, zero payer. So relayers have no economic reason to pick them up, and the only thing that keeps them flowing today is altruism."* [4](#0-3) 

The proposed/implemented mitigation, `OutboundRequestDeliveryReward`, is a `StorageMap` keyed by `source_module_id` that **defaults to zero**, and "zero" is explicitly overloaded to mean both "no reward" and "module not on the allowlist" [5](#0-4)  — this mirrors the same storage/claim design summarized in the doc [6](#0-5) . Nothing forces governance to set a non-zero reward for every module that dispatches system messages; until `set_outbound_request_delivery_reward` is called for a given `module_id`, delivery of that module's messages remains purely altruistic [7](#0-6) .

This is structurally identical to the DYAD bug class: a required-but-unprofitable action (liquidation / message relay) has no reliable economic incentive, and the acknowledged fallback is manual/privileged intervention (team self-liquidates / governance must set a reward and relayers must act "out of altruism").

### Impact Explanation
If a module's outbound reward is left at the default zero (e.g., not yet configured, forgotten during a new pallet rollout, or deliberately kept low), permissionless profit-driven relayers — per Hyperbridge's own economic model, where relayers are described as "profit-driven mediators [who] prioritize messages with fees that ensure profitability" [8](#0-7)  — have no reason to deliver these messages. Concretely:
- Host-parameter updates (e.g., manager rotation) dispatched via `update_host_params` may never reach the destination EVM host, stalling protocol configuration changes indefinitely.
- Relayer fee-withdrawal requests dispatched via `withdrawal.rs` may never be delivered to the destination host manager, **permanently freezing the relayer's own earned funds** since the payout only settles when the ISMP request lands on the destination chain.
- Intents-coprocessor responses and token-governor messages can similarly stall, freezing intent settlement or governance actions.

This satisfies "concrete...permanent freezing of funds" and "a route unable to deliver messages."

### Likelihood Explanation
High likelihood in practice for any module whose `source_module_id` reward has not been explicitly configured by governance, since the reward map defaults to zero and there is no enforced invariant that every dispatching pallet has a corresponding non-zero entry. Because delivery has no cost to skip and no penalty for relayers, rational relayers will simply never pick up these messages, exactly as acknowledged in the design doc.

### Recommendation
- Require that every pallet dispatching hyperbridge-originated requests either attaches a real fee (from a system-owned account) at dispatch time, or that governance is forced to set a non-zero `OutboundRequestDeliveryReward` for that `module_id` before the module is allowed to dispatch (fail-closed rather than fail-open/altruism-dependent).
- For the relayer withdrawal path specifically, consider a permissionless self-relay/self-timeout fallback so a relayer is never solely dependent on third-party altruism to retrieve their own earned funds.
- Add monitoring/alerts for `OutboundRequestsClaimed` staleness per module so an unconfigured or under-rewarded module is detected before requests pile up undelivered.

### Proof of Concept
1. Deploy a new pallet (or leave an existing one, e.g. `pallet-intents-coprocessor`) with `OutboundRequestDeliveryReward[module_id] == 0` (the default, unset by governance).
2. Trigger `update_host_params` or the relayer's `withdraw` extrinsic, which dispatches a `PostRequest` with `FeeMetadata { payer: 0, fee: 0 }` [9](#0-8) .
3. Observe that `process_outbound_request_delivery_claim` rejects any claim for this module at step 6 (allowlist lookup) because `reward == 0` [10](#0-9) , so no rational relayer submits proof, and the request/withdrawal never completes on the destination chain — funds (relayer fees) or state updates (host params) remain stuck indefinitely.

### Citations

**File:** modules/pallets/ismp/src/dispatcher.rs (L97-106)
```rust
		// collect payment for the request
		if fee.fee != Zero::zero() {
			T::Currency::transfer(
				&fee.payer,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| IsmpError::Custom(format!("Error withdrawing request fees: {err:?}")))?;
		}
```

**File:** modules/pallets/host-executive/src/lib.rs (L213-231)
```rust
			let body = inner.abi_encode_with_variant().map_err(|_| Error::<T>::DispatchFailed)?;

			let post = DispatchPost {
				dest: state_machine,
				from: PALLET_ID.to_bytes(),
				to: current_manager.0.to_vec(),
				timeout: 0,
				body,
			};

			let updated = HostParam::EvmHostParam(inner);

			let dispatcher = <T as Config>::IsmpHost::default();
			dispatcher
				.dispatch_request(
					DispatchRequest::Post(post),
					FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() },
				)
				.map_err(|_| Error::<T>::DispatchFailed)?;
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L16-30)
```rust
//! Relayer fee withdrawal.
//!
//! Once fees have been accumulated into [`crate::pallet::Fees`] by
//! [`crate::accumulate`], relayers withdraw them via [`Pallet::withdraw`].
//! The flow:
//!
//! 1. The relayer signs a `(nonce, dest_chain, beneficiary?)` payload with their per-chain key (EVM
//!    secp256k1 / sr25519 / ed25519).
//! 2. The pallet verifies the signature, increments the per-relayer nonce, and dispatches an ISMP
//!    POST request to the destination's host manager (EVM) or `HYPERBRIDGE_MODULE_ID` (substrate)
//!    instructing it to disburse `available_amount` of the fee token to the beneficiary.
//! 3. The `Fees` entry is zeroed so the same balance cannot be withdrawn twice.
//!
//! The on-chain effect is just dispatching the message; the destination chain settles the
//! payout when the ISMP request is delivered there.
```

**File:** docs/outbound-request-incentivization.md (L9-11)
```markdown
A regular cross-chain message that flows *through* hyperbridge has a fee attached at origin (the source chain transfers `fee.payer → RELAYER_FEE_ACCOUNT` and records `RequestPayments[commitment]` in pallet-hyperbridge's child trie). When a relayer delivers and the destination receipt lands back on hyperbridge, the existing `accumulate_fees` flow credits that fee to the relayer. That whole pipeline assumes a *user* paid at origin.

But hyperbridge itself originates requests too: host parameter propagation, host-executive updates, intents-coprocessor responses, token-governor messages, the relayer pallet's withdrawal request. Today these all dispatch with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }` (see `modules/pallets/host-executive/src/lib.rs:228`, `modules/pallets/intents-coprocessor/src/lib.rs:486`, `modules/pallets/relayer/src/lib.rs:638`, and `modules/pallets/token-governor/src/impls.rs`). Zero fee, zero payer. So relayers have no economic reason to pick them up, and the only thing that keeps them flowing today is altruism.
```

**File:** docs/outbound-request-incentivization.md (L40-49)
```markdown
#[pallet::storage]
pub type OutboundRequestDeliveryReward<T: Config> =
    StorageMap<_, Blake2_128Concat, BoundedVec<u8, ModuleIdBound>, BalanceOf<T>, ValueQuery>;

// Idempotency. Presence of `commitment` means some relayer already
// collected the reward for delivering this request.
#[pallet::storage]
pub type OutboundRequestsClaimed<T: Config> =
    StorageMap<_, Blake2_128Concat, H256, (), OptionQuery>;
```
```

**File:** docs/outbound-request-incentivization.md (L126-126)
```markdown
6. **Allowlist lookup.** `reward = OutboundRequestDeliveryReward::<T>::get(module_id)`. If zero, reject. This is the only place the allowlist is enforced; governance enables a module by setting a non-zero reward.
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L1-1)
```rust
// Copyright (C) Polytope Labs Ltd.
```

**File:** modules/pallets/relayer/src/lib.rs (L433-450)
```rust
		/// Governance-set per-`module_id` reward for delivering a
		/// hyperbridge-originated request from that module. Setting
		/// `amount = 0` removes the module from the allowlist.
		#[pallet::call_index(6)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(0, 1))]
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

**File:** docs/content/developers/polkadot/fees.mdx (L21-23)
```text
| **Proof verification cost** | For a cross-chain message to be delivered and executed, it must first be authenticated through state proofs. The expected cost for state proof verification on EVM chains is ~150k gas. Modules should account for this cost when setting the relayer fee. |
| **Message execution gas cost** | After proof verification, the receiving module is handed the request to be executed. This will consume some gas which should also be accounted for. |
| **Relayer service fee** | This additional amount rewards relayers for their services. Relayers are profit-driven mediators and they will prioritize messages with fees that ensure profitability. |
```
