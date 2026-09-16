## Finding [1](#0-0) 

### Title
Relayer fee withdrawal requests dispatch with zero fee and no timeout, permanently freezing already-zeroed fee balances if delivery never lands - (File: `modules/pallets/relayer/src/withdrawal.rs`)

### Summary
`pallet-ismp-relayer`'s `withdraw` function zeroes a relayer's accumulated `Fees` balance and dispatches a cross-chain `PostRequest` to actually pay it out — but that request is dispatched with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }` (zero relayer incentive) and `timeout: 0` (never expires/refunds). This mirrors the Curve `H-8` root cause — a hardcoded/default parameter that silently breaks the claim path for value that a user is entitled to — except here the consequence is permanent, unrecoverable loss of a relayer's earned fees rather than merely "unclaimed rewards."

### Finding Description
When a relayer calls `withdraw_fees` (an unsigned, `ensure_none`-origin extrinsic reachable by any relayer holding a valid signature), `Pallet::withdraw` in [2](#0-1)  does the following, in order:

1. Verifies the relayer's signature and reads `available_amount` from `Fees::<T>`.
2. Builds a `DispatchPost` with `timeout: 0` [3](#0-2) .
3. Dispatches it with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }` — i.e., zero fee, zero payer [4](#0-3) .
4. **Immediately after dispatch succeeds** (before any destination delivery confirmation), zeroes the relayer's local balance: `Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero())` [5](#0-4) , and increments `Nonce` [6](#0-5) .

This design has two compounding defects that are structurally identical in spirit to the Curve bug (a default/hardcoded parameter silently disables the reward/claim mechanism):

- **Zero-fee dispatch removes third-party relayer incentive.** The project's own design document confirms this exact dispatch site is one of several that "dispatch with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }`... Zero fee, zero payer. So relayers have no economic reason to pick them up, and the only thing that keeps them flowing today is altruism." [7](#0-6) . The mitigation built for this (`OutboundRequestDeliveryReward`) is **opt-in per module and defaults to zero** — "`0` (the default) means both 'no reward' and 'module not on the allowlist'" [8](#0-7)  — so unless governance has explicitly registered the relayer pallet's own module id with a non-zero reward, no one is economically motivated to relay this withdrawal message besides the withdrawing relayer itself.
- **`timeout: 0` means the request never expires and can never be refunded.** Per the protocol's own documentation, "If the timeout is set to 0... Messages will never expire" [9](#0-8) . Refunds on the source chain only occur through the timeout pipeline (`on_request_timeout`), as demonstrated in the pallet-ismp fee/refund test [10](#0-9) . Since this request is dispatched with `timeout_timestamp = 0`, that refund path can never fire.

Because `Fees` accounting is zeroed **at dispatch time**, not at confirmed delivery time, and the dispatched message has no economic incentive for third-party relayers and no timeout/refund mechanism, any failure to deliver the withdrawal `PostRequest` to the destination (the delivering relayer goes offline, loses destination-chain gas funds, the destination `HostManager.withdraw` call reverts due to malformed `WithdrawalParams`, the destination host is frozen, etc.) results in the relayer's already-accrued fee balance being **permanently and irrecoverably lost**, with no retry path (the balance is already zero and the nonce already advanced, so a duplicate withdrawal cannot be resubmitted for the same funds).

### Impact Explanation
This is a direct freezing-of-funds bug for relayers, the primary class of Hyperbridge economic actor that this scope explicitly covers ("relayer fee and reward accounting"). A relayer's entire accrued balance for a given `(dest_chain, address)` pair can be wiped out with no possibility of recovery if the corresponding zero-fee, zero-timeout withdrawal message is never successfully delivered to the destination.

### Likelihood Explanation
Reachable from a single, ordinary, unprivileged extrinsic (`withdraw_fees`) that every honest relayer periodically calls as part of normal operation, as documented in the relayer withdrawal flow [11](#0-10) . No malicious governance, admin, or collator action is required — only an ordinary delivery failure or the (protocol-acknowledged) lack of third-party relayer incentive for these zero-fee system messages.

### Recommendation
- Do not zero `Fees` until the withdrawal `PostRequest` delivery is confirmed on the destination (e.g., mirror the pattern used for user-funded requests, where refund/settlement happens against delivery/timeout evidence, not at dispatch time).
- Give relayer withdrawal requests a bounded, non-zero timeout so failed/undelivered withdrawals refund the relayer's on-chain balance via `on_request_timeout`.
- Attach a genuine relayer fee (or ensure `OutboundRequestDeliveryReward` is pre-configured with a non-zero value for the relayer pallet's module id by default) so third-party relayers are economically incentivized to deliver these system withdrawal messages instead of relying on the withdrawing relayer to self-relay.

### Proof of Concept
1. Relayer accrues `Fees::<T>[dest_chain][address] = 250 * 10^18` via `accumulate_fees`.
2. Relayer calls `withdraw_fees` with a valid signature; `Pallet::withdraw` dispatches the `PostRequest` with `fee: Default::default()`, `payer: [0u8;32]`, `timeout: 0` [4](#0-3) , then sets `Fees::<T>[dest_chain][address] = 0` [5](#0-4) .
3. No third-party relayer has an incentive to deliver this zero-fee message (confirmed by the project's own admission at [7](#0-6) ), and the module id is not on the `OutboundRequestDeliveryReward` allowlist by default.
4. Assume the relayer itself cannot complete delivery (loses destination-chain gas, network issue, or the manager contract call reverts).
5. Because `timeout_timestamp = 0`, `on_request_timeout` never fires on Hyperbridge, so the balance is never restored.
6. The relayer's 250-token balance is permanently lost; `withdraw_fees` cannot be called again to recover it since `Fees` is already `0` and `Nonce` was already incremented.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L81-187)
```rust
	pub fn withdraw(withdrawal_data: WithdrawalInputData) -> DispatchResult {
		let address = match &withdrawal_data.signature {
			Signature::Evm { address, .. } => address.clone(),
			Signature::Sr25519 { public_key, .. } => public_key.clone(),
			Signature::Ed25519 { public_key, .. } => public_key.clone(),
		};

		let nonce = Nonce::<T>::get(address.clone(), withdrawal_data.dest_chain);
		let msg = message(nonce, withdrawal_data.dest_chain, withdrawal_data.beneficiary.clone());

		match &withdrawal_data.signature {
			Signature::Evm { address, .. } => {
				let eth_address = withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
				if &eth_address != address {
					Err(Error::<T>::InvalidPublicKey)?
				}
			},
			Signature::Sr25519 { .. } => {
				// Verify signature with public key provided in signature enum
				withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
			},
			Signature::Ed25519 { .. } => {
				// Verify signature with public key provided in signature enum
				withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
			},
		};
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

**File:** docs/outbound-request-incentivization.md (L9-11)
```markdown
A regular cross-chain message that flows *through* hyperbridge has a fee attached at origin (the source chain transfers `fee.payer → RELAYER_FEE_ACCOUNT` and records `RequestPayments[commitment]` in pallet-hyperbridge's child trie). When a relayer delivers and the destination receipt lands back on hyperbridge, the existing `accumulate_fees` flow credits that fee to the relayer. That whole pipeline assumes a *user* paid at origin.

But hyperbridge itself originates requests too: host parameter propagation, host-executive updates, intents-coprocessor responses, token-governor messages, the relayer pallet's withdrawal request. Today these all dispatch with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }` (see `modules/pallets/host-executive/src/lib.rs:228`, `modules/pallets/intents-coprocessor/src/lib.rs:486`, `modules/pallets/relayer/src/lib.rs:638`, and `modules/pallets/token-governor/src/impls.rs`). Zero fee, zero payer. So relayers have no economic reason to pick them up, and the only thing that keeps them flowing today is altruism.
```

**File:** modules/pallets/relayer/src/lib.rs (L169-174)
```rust
	/// Per-`module_id` reward, in the runtime's [`Config::Currency`], paid to
	/// the relayer that delivers a hyperbridge-originated request from that
	/// module to a destination. `0` (the default) means both "no reward" and
	/// "module not on the allowlist". Governance enables a module by setting a
	/// non-zero value.
	#[pallet::storage]
```

**File:** docs/content/developers/polkadot/dispatching.mdx (L53-53)
```text
| `timeout` | Time in seconds for message validity eg 3600 for a timeout of 1 hour, or 0 for no timeout. ie Messages will never expire. If the timeout is set to a non-zero value, messages that have exceeded this timeout will be rejected on the destination and require user action (timeout message) to revert changes. |
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L460-471)
```rust
		// Reproduce the timeout pipeline: delete the commitment, run the
		// module callback, then let the host settle the refund.
		let meta = host.delete_request_commitment(&request).unwrap();
		host.ismp_router()
			.module_for_id(vec![])
			.unwrap()
			.on_timeout(request.clone())
			.unwrap();
		host.on_request_timeout(&request, meta).unwrap();

		// money should've been refunded to the account
		assert_eq!(Balances::balance(&account), 10 * UNIT);
```

**File:** docs/content/developers/network/relayer.mdx (L757-768)
```text
### Initiating withdrawals

To initiate a withdrawal from hyperbridge, a relayer needs to submit a transaction to hyperbridge which triggers the withdrawal request. This extrinsic is unsigned and will not require any native tokens for execution fees. Once the extrinsic is executed, hyperbridge dispatches a POST request that when executed on its destination, will provide the relayer with the fees they've accrued. The relayer account must have sufficient funds to deliver this request to its destination chain.

<br />
Run the `withdraw` subcommand to execute a single end-to-end withdrawal
pass and exit:

```bash lineNumbers
tesseract --config=$HOME/config.toml --db=$HOME/tesseract.db withdraw
```

```
