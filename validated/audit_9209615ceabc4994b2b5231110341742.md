### Title
Relayer fee withdrawal dispatches with hardcoded zero relayer fee, leaving the outbound settlement message economically stranded - ([File: modules/pallets/relayer/src/withdrawal.rs])

### Summary
`pallet-relayer`'s `withdraw` function, which lets a relayer claim their accumulated cross-chain delivery fees, dispatches the ISMP POST request that instructs the destination chain to pay out the relayer with a hardcoded zero relayer fee and a zero-address payer. This is directly analogous to the reported `L1ECOBridge` issue: a hardcoded `0` value on a message dispatch parameter that is meant to guarantee delivery/execution of a critical follow-up message, silently defeating the incentive that makes that delivery happen.

### Finding Description
When a relayer wants to withdraw fees they've earned for delivering messages, they call `Pallet::withdraw` (`modules/pallets/relayer/src/withdrawal.rs`). After verifying the relayer's signature and zeroing the local `Fees` balance, the pallet dispatches a cross-chain `DispatchPost` to the destination chain's host manager (EVM) or `HYPERBRIDGE_MODULE_ID` (Substrate) instructing it to pay out `available_amount`: [1](#0-0) 

Note that:
- `fee: Default::default()` — the relayer fee on this dispatch is hardcoded to zero.
- `payer: [0u8; 32].into()` — the payer is the zero account, so no meaningful account is charged or eligible for a timeout refund.

This pipeline is confirmed as a known, unresolved gap by the repository's own design document, which explicitly calls out this exact code path (and sibling dispatch sites in `host-executive` and `intents-coprocessor`) as dispatching with zero fee/payer, meaning no relayer has an economic incentive to deliver the message: [2](#0-1) 

The local state change (`Fees::<T>::insert(..., U256::zero())`) happens unconditionally once the ISMP dispatch call succeeds, i.e., once the request commitment is recorded — it does not wait for actual cross-chain delivery: [3](#0-2) 

Because the relayer's balance is already zeroed at dispatch time, and the outbound POST carries no incentive for any third-party relayer to pick it up and deliver it to the destination chain, the withdrawal message can sit undelivered indefinitely. Unlike a normal user-originated `DispatchPost` (which is expected to carry a non-zero `fee` collected from `msg.sender`/`payer` per `evm/src/core/EvmHost.sol`'s `dispatch()` and the documented `IsmpDispatcher::dispatch_request` fee model), this system-originated message is exempt from that fee mechanism by construction.

### Impact Explanation
This breaks the relayer reward/withdrawal accounting flow, which is explicitly in scope. A relayer that has earned fees for delivering messages calls `withdraw`, their local `Fees` entry is zeroed, but the actual payout message to the destination chain relies purely on altruistic relaying rather than economic incentive. If no relayer picks up the message (which is the expected steady state absent altruism, since the fee is deliberately zero), the relayer's earned funds are never disbursed on the destination chain — a permanent loss/freezing of the relayer's rewards, since the source-side accounting has already been cleared and cannot be replayed. This is a Medium-severity fund-freezing issue matching the "relayer fee and reward accounting" scope explicitly named in the validation rules.

### Likelihood Explanation
Likelihood is high in principle because it requires no attacker action — it's a direct consequence of the hardcoded value on every single withdrawal. It is only masked today by relayers/operators altruistically delivering these zero-fee system messages, as acknowledged by the project's own internal documentation, which proposes a remediation (a separate reward-claim mechanism) precisely because this gap causes real economic risk to withdrawal delivery reliability. Any reduction in altruistic relaying (e.g., relayer competition, congestion, or simple absence of interested third parties) directly manifests as stuck relayer fee withdrawals.

### Recommendation
Do not zero the payer/fee on the outbound `withdraw` dispatch. Either:
1. Charge a real relayer fee (funded from the withdrawing relayer's own withdrawal amount or protocol treasury) so `RequestPayments`/`accumulate_fees` can reward whichever relayer delivers it, mirroring the fee model used for user-originated dispatches; or
2. Adopt the design already sketched in `docs/outbound-request-incentivization.md` — a dedicated `OutboundRequestDeliveryReward`/claim mechanism keyed by `source_module_id`, paid from the treasury against a destination state proof of delivery, applied to this `MODULE_ID` dispatch and the sibling `host-executive`/`intents-coprocessor` dispatch sites.
3. Additionally, consider not clearing `Fees::<T>` until delivery is confirmed (or track "in-flight withdrawal" state) so a failed/undelivered dispatch does not permanently erase the relayer's claim on those funds.

### Proof of Concept
1. Relayer accumulates `Fees::<T>::get(dest_chain, relayer_address) >= MinWithdrawal`.
2. Relayer submits a signed `WithdrawalInputData` via `Pallet::withdraw`.
3. The pallet zeroes `Fees::<T>` for that relayer/chain and dispatches a `DispatchPost` with `fee: 0, payer: [0u8;32]` (`modules/pallets/relayer/src/withdrawal.rs:161-177`).
4. No third-party relayer has economic incentive to fetch proofs and deliver this POST request to the destination chain (confirmed by `docs/outbound-request-incentivization.md`, which states this is the current, unresolved state of the system).
5. If no altruistic relayer delivers it, the withdrawal message never reaches the destination chain's host manager; the relayer's fee balance is already zero on the source chain, and the payout never lands on the destination chain — funds are permanently unrecoverable through the intended withdrawal path.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L116-187)
```rust
		let available_amount = Fees::<T>::get(withdrawal_data.dest_chain, address.clone());

		if available_amount <
			Self::min_withdrawal_amount(withdrawal_data.dest_chain)
				.unwrap_or(MinWithdrawal::get())
		{
			Err(Error::<T>::NotEnoughBalance)?
		}

		let dispatcher = <T as Config>::IsmpHost::default();

		Nonce::<T>::try_mutate(address.clone(), withdrawal_data.dest_chain, |value| {
			*value += 1;
			Ok::<(), ()>(())
		})
		.map_err(|_| Error::<T>::ErrorCompletingCall)?;

		let beneficiary_address = withdrawal_data.beneficiary.clone().unwrap_or(address.clone());
		let (to, body) = match withdrawal_data.dest_chain {
			s if s.is_substrate() => (
				HYPERBRIDGE_MODULE_ID.to_vec(),
				Message::WithdrawRelayerFees(WithdrawalRequest {
					amount: available_amount.low_u128(),
					account: AccountId32::try_from(&beneficiary_address[..])
						.map_err(|_| Error::<T>::InvalidPublicKey)?,
				})
				.encode(),
			),
			_ => {
				let HostParam::EvmHostParam(params) =
					HostParams::<T>::get(withdrawal_data.dest_chain)
						.ok_or_else(|| Error::<T>::MissingMangerAddress)?;

				let body = WithdrawalParams {
					beneficiary_address: beneficiary_address.clone(),
					amount: available_amount.into(),
					token: params.fee_token,
				}
				.abi_encode()
				.map_err(|_| Error::<T>::InvalidPublicKey)?;

				(params.host_manager.0.to_vec(), body)
			},
		};

		let post = DispatchPost {
			dest: withdrawal_data.dest_chain,
			from: MODULE_ID.to_vec(),
			to,
			body,
			timeout: 0,
		};

		// Account is not useful in this case
		dispatcher
			.dispatch_request(
				DispatchRequest::Post(post),
				FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() },
			)
			.map_err(|_| Error::<T>::DispatchFailed)?;

		Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero());

		Self::deposit_event(Event::<T>::Withdraw {
			address: sp_runtime::BoundedVec::truncate_from(address.clone()),
			beneficiary_address: sp_runtime::BoundedVec::truncate_from(beneficiary_address),
			state_machine: withdrawal_data.dest_chain,
			amount: available_amount,
		});

		Ok(())
	}
```

**File:** docs/outbound-request-incentivization.md (L7-21)
```markdown
## The problem

A regular cross-chain message that flows *through* hyperbridge has a fee attached at origin (the source chain transfers `fee.payer → RELAYER_FEE_ACCOUNT` and records `RequestPayments[commitment]` in pallet-hyperbridge's child trie). When a relayer delivers and the destination receipt lands back on hyperbridge, the existing `accumulate_fees` flow credits that fee to the relayer. That whole pipeline assumes a *user* paid at origin.

But hyperbridge itself originates requests too: host parameter propagation, host-executive updates, intents-coprocessor responses, token-governor messages, the relayer pallet's withdrawal request. Today these all dispatch with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }` (see `modules/pallets/host-executive/src/lib.rs:228`, `modules/pallets/intents-coprocessor/src/lib.rs:486`, `modules/pallets/relayer/src/lib.rs:638`, and `modules/pallets/token-governor/src/impls.rs`). Zero fee, zero payer. So relayers have no economic reason to pick them up, and the only thing that keeps them flowing today is altruism.

## The shape of the solution

The issue creator's preferred shape ([comment 4428807013](https://github.com/polytope-labs/hyperbridge/issues/532#issuecomment-4428807013)): use `pallet-relayer` to pay BRIDGE to whoever proves they delivered a hyperbridge-originated request. The messaging task in the tesseract relayer submits the claim.

Not every pallet on hyperbridge that dispatches a request is in scope. `pallet_ismp::child_trie::RequestCommitments` ends up holding commitments for every successful dispatch via `IsmpDispatcher`, which includes both the system messages we want to incentivize (host-executive, intents-coprocessor, token-governor, the relayer pallet's withdrawal path, future modules like bandwidth) and any other pallet that ends up dispatching from hyperbridge. The reward storage is therefore keyed by `source_module_id` and only modules with a non-zero reward are eligible. The `module_id` is the `from` field on the `PostRequest`, which each pallet sets to its unique module identifier. A module with zero reward is treated as not on the allowlist and rejected before any state proof verification runs.

This is structurally identical to the existing `claim_outbound_consensus_delivery_reward` (see `modules/pallets/relayer/src/outbound_consensus.rs`) on the consensus side. The request claim lives in its own `modules/pallets/relayer/src/outbound_request.rs` module that mirrors it: swap "consensus rotation delivered" for "request delivered," key the reward storage by `module_id`, and have the relayer ship the full `PostRequest` in the claim so the pallet can hash it on chain.

No changes to pallet-hyperbridge or to any of the system-message dispatch sites. The reward is decoupled from the dispatch path and paid out at claim time against a destination state proof.
```
