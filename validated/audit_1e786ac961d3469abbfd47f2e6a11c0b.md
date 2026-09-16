## Analog Found

### Title
Missing chain-binding in `SubstrateCalldata` signature enables cross-chain replay of authorized runtime calls - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
The `hyper-fungible-token` pallet's `on_accept` handler executes an attacker-controlled `runtime_call` on behalf of a `beneficiary` account whenever a cross-chain token message includes optional calldata with a `MultiSignature`. The signed payload that authorizes this privileged action is `(nonce, runtime_call)` with no chain identifier, genesis hash, or pallet/contract instance bound into it — the exact same "raw hash, no domain separator" pattern the external report flags for `BatcherPaymentService`.

### Finding Description
In `on_accept`, when `message.data` decodes to a `SubstrateCalldata` with a `signature`, the pallet verifies the signature over: [1](#0-0) 

For all three signature schemes (Ed25519, Sr25519, Ecdsa) the signed message is built as `(nonce, substrate_data.runtime_call.clone()).encode()` — nothing else. There is no chain id, genesis hash, `StateMachine` identifier, source/destination contract address, or any other domain separator mixed into the hash, unlike EIP-712-style or genesis-hash-bound Substrate signatures that are the norm precisely to stop this class of bug.

`SubstrateCalldata` is decoded straight from `message.data`, which is part of the ABI-encoded `Message` struct dispatched from the source EVM chain's HyperFungibleToken contract: [2](#0-1) [3](#0-2) 

Any unprivileged token bridger who calls the source-chain bridge contract's send function fully controls the `data` field of their own transfer, and this field (including a previously observed `runtime_call`/`signature` pair) is delivered verbatim to whichever destination pallet accepts the registered `(source, from)` contract pair: [4](#0-3) 

Because the same token contract/asset is commonly registered as a trusted source on multiple destination parachains (the repo's own `gargantua` and `nexus` runtimes both configure this pallet against `ContractToAsset`/`ChainConfig` entries), a `(nonce, runtime_call, signature)` triple observed in one legitimately-delivered cross-chain message can be copied into a new transfer's `data` field and routed to a second destination chain running the same pallet. If the beneficiary's on-chain nonce on that second chain happens to equal the nonce baked into the harvested signature (trivially true for any account that has never transacted there, i.e. nonce `0`), the pallet will accept the stale signature and dispatch the same `runtime_call` with `RawOrigin::Signed(beneficiary)`: [5](#0-4) 

This lets an unprivileged relayer/bridger force a victim's previously-authorized call to execute a second time, as the victim, on a chain the victim never intended to interact with — a direct analog of the reported cross-network signature replay: no domain separator binds the authorization to one specific chain/pallet instance.

### Impact Explanation
Successful replay causes an "unauthorized app action": an arbitrary `runtime_call` (subject only to `BaseCallFilter`) is dispatched with the victim account as origin on a chain it was never signed for. Depending on the call, this can move funds, vote, bond/unbond stake, or invoke any other filtered-in dispatchable under the victim's identity without their consent on that chain — a forged-authorization / unauthorized-action class issue reachable from a single crafted token-bridge transfer.

### Likelihood Explanation
The attacker only needs (a) to observe a previously delivered message's `data` field (public via chain history/ISMP commitments), and (b) to trigger a new transfer to a destination chain that also runs this pallet with a matching source-contract registration and a beneficiary nonce coincidence (commonly true for accounts that have not yet transacted there). No privileged role, governance, or key compromise is required — matching the "unprivileged token bridger" reachable-path requirement.

### Recommendation
Bind the signed payload to a full domain separator before hashing, analogous to EIP-712 domain separation: include the destination `StateMachine`/chain identifier (or genesis hash), the pallet/instance address, and ideally the source `(source, from)` pair, e.g. `(GENESIS_HASH_OR_CHAIN_ID, PALLET_ACCOUNT, nonce, runtime_call).encode()`, for all three signature branches (`Ed25519`, `Sr25519`, `Ecdsa`) in `on_accept`.

### Proof of Concept
1. Victim signs `(nonce=0, runtime_call=X)` off-chain and includes it as `SubstrateCalldata` in a legitimate transfer's `data`, dispatched from EVM `TokenContract` to Chain A's `hyper-fungible-token` pallet; it executes successfully as `beneficiary`, incrementing nonce to 1.
2. Attacker observes this `data` payload (public request body) and copies the exact `signature`/`runtime_call` bytes.
3. Attacker calls the same `TokenContract` (or an equivalent contract registered as a trusted source on Chain B) to send tokens to the same `beneficiary`, embedding the copied `data`.
4. Chain B's `hyper-fungible-token` pallet independently computes `nonce = account_nonce(beneficiary)` (still `0` on Chain B, a chain the victim has never used), recomputes `keccak256((0, X).encode())`, successfully verifies the harvested signature, and dispatches `runtime_call X` with `RawOrigin::Signed(beneficiary)` on Chain B — an action the victim never authorized for Chain B.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L54-56)
```rust
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L128-171)
```rust
				let nonce = frame_system::Pallet::<T>::account_nonce(beneficiary.clone());

				match multi_signature {
					MultiSignature::Ed25519(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let msg = sp_io::hashing::keccak_256(&payload);
						let pub_key = beneficiary_bytes
							.as_slice()
							.try_into()
							.map_err(|_| HftError::SignatureVerificationFailed)?;
						if !sp_io::crypto::ed25519_verify(&sig, msg.as_ref(), &pub_key) {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
					MultiSignature::Sr25519(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let msg = sp_io::hashing::keccak_256(&payload);
						let pub_key = beneficiary_bytes
							.as_slice()
							.try_into()
							.map_err(|_| HftError::SignatureVerificationFailed)?;
						if !sp_io::crypto::sr25519_verify(&sig, msg.as_ref(), &pub_key) {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
					MultiSignature::Ecdsa(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let preimage = vec![
							format!("{ETHEREUM_MESSAGE_PREFIX}{}", payload.len())
								.as_bytes()
								.to_vec(),
							payload,
						]
						.concat();
						let msg = sp_io::hashing::keccak_256(&preimage);
						let pub_key = sp_io::crypto::secp256k1_ecdsa_recover(&sig.0, &msg)
							.map_err(|_| HftError::EcdsaRecoveryFailed)?;
						let eth_address =
							H160::from_slice(&sp_io::hashing::keccak_256(&pub_key[..])[12..]);
						let substrate_account = T::EvmToSubstrate::convert(eth_address);
						if substrate_account != beneficiary {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
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

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L33-43)
```rust
// ABI-compatible Message matching the Solidity HyperFungibleToken.Message struct:
// struct Message { bytes from; bytes to; uint256 amount; bytes data; }
alloy_sol_macro::sol! {
	#![sol(all_derives)]
	struct Message {
		bytes from;
		bytes to;
		uint256 amount;
		bytes data;
	}
}
```

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L105-113)
```rust
/// SCALE-encoded calldata for executing a runtime call on the destination substrate chain
#[derive(Debug, Clone, Encode, Decode, scale_info::TypeInfo, PartialEq, Eq)]
pub struct SubstrateCalldata {
	/// Optional SCALE-encoded [MultiSignature](sp_runtime::MultiSignature) of the beneficiary's
	/// account nonce and the encoded runtime call
	pub signature: Option<Vec<u8>>,
	/// SCALE-encoded runtime call to execute
	pub runtime_call: Vec<u8>,
}
```
