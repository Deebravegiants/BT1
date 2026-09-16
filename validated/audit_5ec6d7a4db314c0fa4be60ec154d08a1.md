### Title
Unsigned cross-chain calldata lets an attacker dispatch arbitrary runtime calls under an impersonated origin - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler SCALE-decodes an attacker-supplied byte blob into a `T::RuntimeCall` — the runtime's top-level, universal call enum covering every pallet dispatchable — and then dispatches it. This mirrors the GHSA-324h-2v7h-q3xx bug class (an untrusted-input deserializer that can instantiate arbitrary types), except here the "arbitrary type" is any dispatchable in the entire parachain runtime, gated only by `BaseCallFilter`, and the *origin* used for dispatch can be attacker-chosen when no signature accompanies the calldata.

### Finding Description
In `modules/pallets/hyper-fungible-token/src/module.rs`, `on_accept` handles an incoming `PostRequest` from a registered peer (EVM or Substrate) contract: [1](#0-0) 

`substrate_data.runtime_call` is fully attacker-controlled bytes carried in the cross-chain `data` field of the ABI-encoded `Message`, which the source-chain sender constructs off-chain in their own `send()` call. When no `signature` is supplied, the dispatch origin is derived directly from `message.from` — also attacker-supplied bytes in the same message — with no cryptographic binding to the actual caller: [2](#0-1) 

The decoded call is then dispatched as that origin, subject only to the runtime's `BaseCallFilter`: [3](#0-2) 

`T::RuntimeCall::decode` will happily construct *any* variant the runtime enum supports (Balances, Assets, Ismp, Treasury, Sudo-adjacent pallets if present, etc.) from attacker bytes — this is structurally the same class of bug as an unrestricted YAML/object deserializer: the input fully controls which concrete "type" (call variant) gets instantiated and executed, with the only guard being an allow/deny list (`BaseCallFilter`) rather than a safe, restricted decode surface.

Compare this with the harder-scoped path in `modules/pallets/call-decompressor/src/lib.rs`, which decodes runtime calls from unsigned extrinsics but explicitly restricts the *decoded* call to only `pallet_ismp::Call::handle_unsigned` or `pallet_ismp_relayer::Call::accumulate_fees` before executing it: [4](#0-3) 

The HFT module has no such variant allow-list — it will dispatch whatever `T::RuntimeCall` decodes to, as long as `BaseCallFilter` doesn't explicitly reject it.

### Impact Explanation
If the unsigned branch's origin (derived from attacker-controlled `message.from` bytes) is reachable with a `message.from` value the attacker chooses freely, an attacker can:
- Dispatch arbitrary runtime calls as any account of their choosing (impersonation), including transferring balances, minting/burning assets, or invoking other privileged-looking pallet calls that are not blocked by `BaseCallFilter`.
- This can lead to unauthorized app actions, theft of funds, or manipulation of protocol state — matching the "unauthorized app action" / "concrete theft of funds" impact bar.

Severity depends on how permissive the deployed runtime's `BaseCallFilter` is (e.g. `InsideBoth<..., Everything>` combinations were observed in `gargantua`/`nexus` runtimes) and whether the EVM-side `send()` contract truly leaves `from` attacker-controlled rather than binding it to `msg.sender`.

### Likelihood Explanation
Reaching this path only requires calling the publicly permissionless `send()` on the peer `HyperFungibleToken`/`WrappedHyperFungibleToken` contract (or the pallet's own `send`) with a crafted `data` payload — no privileged role needed. The signature-present branch is properly authenticated (Ed25519/Sr25519/ECDSA verified against the beneficiary), so exploitation likelihood hinges entirely on whether the unsigned branch's origin-selection (`message.from`) can be freely chosen by the caller on the source chain, which I could not fully confirm from the available Solidity source (`HyperFungibleToken.sol`) within this investigation — the index did not surface the exact `send()` body enforcing `from == msg.sender`. This should be verified directly against the contract's `send()` implementation before treating this as confirmed-exploitable; if `from` is cryptographically bound to `msg.sender` on all supported source chains, the impersonation vector collapses to "self as origin," which is comparatively low-impact (limited to the sender's own privileges, still bypasses BaseCallFilter-gated dispatch though).

### Recommendation
- Restrict the unsigned dispatch path to a signature-authenticated origin only; do not allow `message.from` bytes to select the account used for `RuntimeCall` dispatch without a cryptographic binding.
- Alternatively, remove the unsigned/no-signature branch's ability to dispatch arbitrary `RuntimeCall`s entirely, or scope it to an explicit allow-list of safe call variants (mirroring the `call-decompressor` pallet's pattern) rather than relying solely on `BaseCallFilter`.
- Verify and, if necessary, harden the EVM-side `send()` implementations (`HyperFungibleToken.sol`, `WrappedHyperFungibleToken.sol`, and their Upgradeable variants) so `message.from` cannot be set to an arbitrary value unrelated to `msg.sender`.

### Proof of Concept
Conceptual (pending confirmation of EVM-side `from` enforcement):
1. Attacker calls `send()` on a registered EVM `HyperFungibleToken` contract, setting `to` to an arbitrary beneficiary bytes value and `data` to a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <encoded privileged call> }`.
2. Attacker sets `from` (in the ABI-encoded `Message`) to the bytes of a victim/target Substrate account they do not control.
3. On delivery, `on_accept` decodes `runtime_call` and dispatches it with `RawOrigin::Signed(<derived from message.from>)`, executing the call as if the victim account authorized it, bounded only by `BaseCallFilter`.

This mirrors the reproduction shown in the pallet's own test `should_receive_asset_with_calldata` (`modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs:255-322`), which demonstrates the mechanics of calldata-driven `RuntimeCall` dispatch via `on_accept`, but that test uses the signed branch; the unsigned/no-signature branch and its origin derivation is the part requiring further confirmation against the live EVM contract code. [5](#0-4)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-123)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L176-187)
```rust
			} else {
				let from_bytes = message.from.as_ref();
				if source.is_evm() {
					T::EvmToSubstrate::convert(H160::from_slice(
						&from_bytes[from_bytes.len() - 20..],
					))
				} else {
					let mut account = [0u8; 32];
					account.copy_from_slice(from_bytes);
					account.into()
				}
			};
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-202)
```rust
			let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
				.map_err(HftError::RuntimeCallDecodeError)?;
			// Apply the runtime's base call filter so that cross-chain calls cannot
			// reach dispatchables that the runtime has otherwise filtered out (e.g.
			// during a maintenance mode or a SafeMode period).
			if !<T as frame_system::Config>::BaseCallFilter::contains(&runtime_call) {
				Err(HftError::CallFiltered)?
			}
			use sp_runtime::traits::Dispatchable;
			runtime_call
				.dispatch(RawOrigin::Signed(origin.clone()).into())
				.map_err(|e| HftError::CallDispatchError(e.error))?;

			frame_system::Pallet::<T>::inc_account_nonce(origin);
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L275-295)
```rust
		if let Some(call) = IsSubType::<pallet_ismp::Call<T>>::is_sub_type(&runtime_call).cloned() {
			match call {
				pallet_ismp::Call::handle_unsigned { messages } =>
					<pallet_ismp::Pallet<T>>::execute(messages)
						.map_err(|_| Error::<T>::ErrorExecutingCall)?,
				_ => Err(Error::<T>::CallNotSupported)?,
			};
		} else if let Some(call) =
			IsSubType::<pallet_ismp_relayer::Call<T>>::is_sub_type(&runtime_call).cloned()
		{
			match call {
				pallet_ismp_relayer::Call::accumulate_fees { withdrawal_proof } =>
					<pallet_ismp_relayer::Pallet<T>>::accumulate_fees(
						frame_system::RawOrigin::None.into(),
						withdrawal_proof,
					)?,
				_ => Err(Error::<T>::CallNotSupported)?,
			};
		} else {
			return Err(Error::<T>::CallNotSupported)?;
		}
```

**File:** modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs (L255-322)
```rust
#[test]
fn should_receive_asset_with_calldata() {
	new_test_ext().execute_with(|| {
		// First send to escrow funds
		let params = SendParams {
			asset_id: HftNativeAssetId::get(),
			destination: StateMachine::Evm(1),
			recipient: BoundedVec::try_from(BOB.as_slice().to_vec()).unwrap(),
			timeout: 0,
			amount: SEND_AMOUNT,
			relayer_fee: Default::default(),
			call_data: None,
		};

		HyperFungibleToken::send(RuntimeOrigin::signed(ALICE), params).unwrap();

		// Build a runtime call: transfer from beneficiary to a final recipient
		let final_recipient = AccountId32::new([5u8; 32]);
		let runtime_call =
			crate::runtime::RuntimeCall::Balances(pallet_balances::Call::transfer_allow_death {
				dest: final_recipient.clone(),
				value: SEND_AMOUNT,
			})
			.encode();

		// Sign with sr25519
		let (pair, ..) = sp_core::sr25519::Pair::generate();
		let beneficiary_bytes = pair.public().0;
		let payload = (0u64, runtime_call.clone()).encode();
		let message_hash = sp_io::hashing::keccak_256(&payload);
		let raw_signature = pair.sign(&message_hash);
		let multisignature = MultiSignature::Sr25519(raw_signature).encode();

		let substrate_data = SubstrateCalldata { signature: Some(multisignature), runtime_call };

		let module = HyperFungibleToken::default();
		let post = PostRequest {
			source: StateMachine::Evm(1),
			dest: StateMachine::Kusama(100),
			nonce: 0,
			from: hft_contract(),
			to: pallet_hyper_fungible_token::PALLET_ID.to_bytes(),
			timeout_timestamp: 1000,
			body: {
				let msg = Message {
					from: alloy_primitives::Bytes::from(vec![0x11u8; 20]),
					to: alloy_primitives::Bytes::from(beneficiary_bytes.to_vec()),
					amount: {
						let bytes = convert_to_erc20(SEND_AMOUNT, 18, 10).to_big_endian();
						alloy_primitives::U256::from_be_bytes(bytes)
					},
					data: alloy_primitives::Bytes::from(substrate_data.encode()),
				};
				Message::abi_encode(&msg)
			},
		};

		module.on_accept(post.clone()).unwrap();

		// The calldata transferred tokens from beneficiary to final_recipient
		let final_balance = pallet_balances::Pallet::<Test>::free_balance(final_recipient);
		assert_eq!(final_balance, SEND_AMOUNT);

		// Replay should fail (nonce incremented)
		let result = module.on_accept(post);
		assert!(result.is_err());
	});
}
```
