### Title
Incorrect Authorization: `pallet-call-decompressor`'s empty `pre_dispatch` skips the runtime's `BaseCallFilter`, letting a permissionless unsigned extrinsic bypass the BEEFY/SP1 consensus gate - (File: `modules/pallets/call-decompressor/src/lib.rs`)

### Summary
The GitLab CVE describes incorrect authorization validation on API endpoints reachable by an unauthenticated caller. The structural analog in Hyperbridge is `pallet-call-decompressor`: the same `BaseCallFilter::contains` check that the runtime relies on to reject dangerous `pallet_ismp::handle_unsigned` batches is only enforced inside `ValidateUnsigned::validate_unsigned` (the mempool/gossip gate), while the pallet's `pre_dispatch` — the hook that actually runs when the extrinsic is applied on-chain — is an intentional no-op.

### Finding Description
`decompress_call` is an unsigned, permissionless extrinsic (`ensure_none(origin)?`) that decompresses an arbitrary encoded `RuntimeCall` and executes it directly via `Self::decode_and_execute(call_bytes)`: [1](#0-0) 

Its `ValidateUnsigned` impl is where the actual safety net lives: it decodes the inner call, checks `T::BaseCallFilter::contains(&runtime_call)`, and only allows the call through if it matches `pallet_ismp::Call::handle_unsigned` or `pallet_ismp_relayer::Call::accumulate_fees`: [2](#0-1) 

But `pre_dispatch` — the check that actually gates *on-chain application* of an unsigned extrinsic in `frame_executive`, as opposed to `validate_unsigned`, which only gates transaction-pool acceptance/gossip — is explicitly empty: [3](#0-2) 

The runtime's `BaseCallFilter = IsmpCallFilter` exists specifically to stop a raw BEEFY consensus update from reaching `pallet_ismp::Call::handle_unsigned` without first passing through `pallet-beefy-consensus-proofs`' SP1 zkVM verification, and to block `fund_message`: [4](#0-3) [5](#0-4) 

This filter is designed to run on every dispatched call, and the project has a dedicated simnode test proving it must be enforced at dispatch, not merely at mempool-validation time, distinguishing `System::CallFiltered` (filter ran) from `BadOrigin` (filter was bypassed and the call body ran): [6](#0-5) 

Because `decompress_call`'s own top-level call (`CallDecompressor::decompress_call`) trivially passes `IsmpCallFilter::contains` (it only matches on `Ismp::handle_unsigned`/`Ismp::fund_message`, not `CallDecompressor::decompress_call`), the runtime-level filter never inspects the *inner* decoded call. The only place that inspects the inner call against `BaseCallFilter` is `validate_unsigned`, which does not gate on-chain execution when `pre_dispatch` is a no-op. As a result, a node that includes this unsigned extrinsic directly in a block (bypassing normal txpool gossip/validation, which any block-producing or malicious/permissive collator/relayer-adjacent submission path can do) can smuggle a `pallet_ismp::Call::handle_unsigned` batch carrying a raw BEEFY consensus message through `decode_and_execute`, without ever tripping the `IsmpCallFilter` gate that the runtime authors explicitly built to prevent this exact bypass.

### Impact Explanation
If the inner call executes without SP1 verification, an attacker can forge a BEEFY consensus/state update, which forges state commitments the whole ISMP stack (state membership/non-membership proofs, token bridge mint/burn, relayer fee accounting, intents escrow) treats as trusted. This can lead to unbacked mint, forged message delivery, or a permanently corrupted consensus state that halts message delivery for the state machine (denial of service matching the DoS framing of the CVE, but with a materially worse consequence given Hyperbridge's trust model).

### Likelihood Explanation
Requires submitting a single unsigned extrinsic that never goes through normal peer-to-peer transaction-pool validation (e.g., a block author directly including it, or any path that calls `pre_dispatch`/apply without first running `validate_unsigned`). This is a realistic path in Substrate's unsigned-extrinsic model since `pre_dispatch` is precisely the hook meant to be the authoritative on-chain gate.

### Recommendation
Move the `BaseCallFilter::contains(&runtime_call)` check (and the allow-list of inner call variants) from `validate_unsigned` into `pre_dispatch`, so it is enforced unconditionally at the point the extrinsic is actually applied, not only when it is being validated for pool/gossip acceptance. Alternatively, have `decode_and_execute` itself re-check `T::BaseCallFilter::contains` immediately before dispatching the decoded `RuntimeCall`.

### Proof of Concept
1. Encode a `pallet_ismp::Call::handle_unsigned { messages: [Message::Consensus(beefy_consensus_msg)] }` targeting the BEEFY consensus client.
2. Compress it and wrap it as `CallDecompressor::decompress_call { compressed, encoded_call_size }`.
3. Submit/include this extrinsic on-chain through any path that reaches `pre_dispatch`/`apply_extrinsic` without going through `validate_unsigned` (e.g. direct block authoring).
4. `pre_dispatch` returns `Ok(())` unconditionally (`modules/pallets/call-decompressor/src/lib.rs:136-139`), so the extrinsic is applied; `decode_and_execute` runs the decoded `handle_unsigned` call directly, bypassing the `IsmpCallFilter` check that `parachain/runtimes/gargantua/src/lib.rs:818-836` / `parachain/runtimes/nexus/src/lib.rs:754-772` intend to enforce, and the raw BEEFY update is processed without SP1 verification.

Note: I was not able to fully inspect the body of `Self::decode_and_execute` (source truncated before I could confirm whether it independently re-checks `BaseCallFilter`). If that function does perform its own filter check, this finding would be mitigated; this could not be fully confirmed within the available search budget, and a full review of `modules/pallets/call-decompressor/src/lib.rs`'s `decode_and_execute`/`decompress` implementation is recommended to close this gap definitively.

### Citations

**File:** modules/pallets/call-decompressor/src/lib.rs (L107-122)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::decompress_call())]
		pub fn decompress_call(
			origin: OriginFor<T>,
			compressed: Vec<u8>,
			encoded_call_size: u32,
		) -> DispatchResult {
			ensure_none(origin)?;
			ensure!(
				encoded_call_size < T::MaxCallSize::get() * ONE_MB,
				Error::<T>::CallSizeOutOfBound
			);
			let call_bytes = Self::decompress(compressed, encoded_call_size)?;
			Self::decode_and_execute(call_bytes)?;
			Ok(())
		}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L136-139)
```rust
		// empty pre-dispatch so we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L141-189)
```rust
		fn validate_unsigned(source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let Call::decompress_call { compressed, encoded_call_size } = call else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};

			let decompressed = Self::decompress(compressed.clone(), encoded_call_size.clone())
				.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;

			let runtime_call = T::RuntimeCall::decode_all_with_depth_limit(
				MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
				&mut &decompressed[..],
			)
			.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;

			if !<T as frame_system::Config>::BaseCallFilter::contains(&runtime_call) {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}

			let provides = if let Some(call) =
				IsSubType::<pallet_ismp::Call<T>>::is_sub_type(&runtime_call).cloned()
			{
				let _: Result<(), TransactionValidityError> = match call {
					pallet_ismp::Call::handle_unsigned { messages: _ } => Ok(()),
					_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
				};

				let ValidTransaction { provides, .. } =
					<pallet_ismp::Pallet<T> as ValidateUnsigned>::validate_unsigned(source, &call)
						.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;

				provides
			} else if let Some(call) =
				IsSubType::<pallet_ismp_relayer::Call<T>>::is_sub_type(&runtime_call).cloned()
			{
				let _: Result<(), TransactionValidityError> = match call.clone() {
					pallet_ismp_relayer::Call::accumulate_fees { withdrawal_proof: _ } => Ok(()),
					_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
				};

				let ValidTransaction { provides, .. } =
					<pallet_ismp_relayer::Pallet<T> as ValidateUnsigned>::validate_unsigned(
						source, &call,
					)
					.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;

				provides
			} else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};
```

**File:** parachain/runtimes/gargantua/src/lib.rs (L808-836)
```rust
/// Gargantua routes all BEEFY consensus updates through `pallet-beefy-consensus-proofs`, which
/// requires each proof to pass SP1 zkVM verification before it can advance the BEEFY state.
/// Allowing raw updates through `handle_unsigned` would bypass that requirement entirely, so
/// any batch that carries a BEEFY consensus message is rejected here. `fund_message` is also
/// disabled because gargantua uses the bandwidth model for request fees; per-message top-ups
/// have no role in that accounting.
///
/// A consensus message only names the state it updates, so we ask the host which client owns
/// that state and compare against BEEFY. Reading from the host remains correct even as more
/// states (Polkadot, Paseo) are bound to the same client over time.
pub struct IsmpCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for IsmpCallFilter {
	fn contains(call: &RuntimeCall) -> bool {
		use ::ismp::{host::IsmpHost, messaging::Message};
		match call {
			RuntimeCall::Ismp(pallet_ismp::Call::fund_message { .. }) => false,
			RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned { messages }) => {
				let host = Ismp::default();
				!messages.iter().any(|message| match message {
					Message::Consensus(consensus) =>
						host.consensus_client_id(consensus.consensus_state_id) ==
							Some(ismp_beefy::BEEFY_CONSENSUS_ID),
					_ => false,
				})
			},
			_ => true,
		}
	}
}
```

**File:** parachain/runtimes/nexus/src/lib.rs (L746-772)
```rust
/// Allowing raw updates through `handle_unsigned` would bypass that requirement entirely, so
/// any batch that carries a BEEFY consensus message is rejected here. `fund_message` is also
/// disabled because it will change the child trie root allowing beefy proofs that have no economic
/// value
///
/// A consensus message only names the state it updates, so we ask the host which client owns
/// that state and compare against BEEFY. Reading from the host remains correct even as more
/// states (Polkadot, Paseo) are bound to the same client over time.
pub struct IsmpCallFilter;
impl Contains<RuntimeCall> for IsmpCallFilter {
	fn contains(call: &RuntimeCall) -> bool {
		use ::ismp::{host::IsmpHost, messaging::Message};
		match call {
			RuntimeCall::Ismp(pallet_ismp::Call::fund_message { .. }) => false,
			RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned { messages }) => {
				let host = Ismp::default();
				!messages.iter().any(|message| match message {
					Message::Consensus(consensus) =>
						host.consensus_client_id(consensus.consensus_state_id) ==
							Some(ismp_beefy::BEEFY_CONSENSUS_ID),
					_ => false,
				})
			},
			_ => true,
		}
	}
}
```

**File:** parachain/simtests/src/base_call_filter.rs (L163-177)
```rust
/// True when the base call filter rejected the call before its body ran.
fn is_call_filtered(err: &DispatchError) -> bool {
	let DispatchError::Module(module) = err else { return false };
	matches!(
		module.details(),
		Ok(details)
			if details.pallet.name() == "System" && details.variant.name.as_str() == "CallFiltered"
	)
}

/// True when the call passed the filter and reached the body, where `ensure_none` rejected
/// the signed origin.
fn is_bad_origin(err: &DispatchError) -> bool {
	matches!(err, DispatchError::BadOrigin)
}
```
