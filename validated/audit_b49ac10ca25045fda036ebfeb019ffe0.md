### Title
Untrusted Cross-Chain Bytes Deserialized Directly into an Executable `RuntimeCall` and Dispatched - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler for incoming ISMP `PostRequest`s SCALE-decodes an optional `data` field carried inside the untrusted, attacker/relayer-supplied ABI `Message` body into a `SubstrateCalldata` struct, and then SCALE-decodes the nested `runtime_call: Vec<u8>` bytes directly into `T::RuntimeCall` — the full dispatchable surface of the chain — before calling `.dispatch(...)`. [1](#0-0) [2](#0-1)  This is the same bug class as GHSA-xfxp-ppx7-cqrp: attacker-controlled bytes are deserialized into an object capable of driving privileged behavior (there, ProtoStream RCE; here, arbitrary runtime-call dispatch), gated only by application-level checks rather than by the ISMP consensus/membership proof that authenticates the message.

### Finding Description
Any account holding (or able to acquire) a registered token can call `send` on the peer `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM contract with an arbitrary `call_data` payload. This payload becomes `message.data` in the ABI `Message` and is delivered as the `body` of an ISMP `PostRequest` once a relayer submits it with a valid state/consensus proof. [3](#0-2) [4](#0-3) 

On the destination chain, `on_accept`:
1. Decodes `message.data` into `SubstrateCalldata { signature: Option<Vec<u8>>, runtime_call: Vec<u8> }` via plain `codec::Decode`. [1](#0-0) 
2. Decodes `substrate_data.runtime_call` into `T::RuntimeCall` — the entire runtime dispatchable enum — again via plain `Decode::decode`. [5](#0-4) 
3. The only gate before dispatch is `BaseCallFilter::contains(&runtime_call)`; there is no allow-list restricting which pallets/calls a cross-chain message may trigger beyond whatever the runtime's base filter excludes. [6](#0-5) 
4. If no `signature` is supplied, the dispatch origin is derived solely from `message.from` (an address supplied inside the ABI-encoded, attacker/contract-constructed message) via `T::EvmToSubstrate::convert`, with **no cryptographic proof that the destination-chain account authorized this specific call** — the ISMP proof only attests that some source-chain contract emitted this event, not that the named account consented to the decoded `RuntimeCall`. [7](#0-6) 

This mirrors the CWE-502 pattern: a nested, attacker-influenced byte blob is deserialized straight into a highly privileged executable type (`RuntimeCall`) and driven to execution, with authorization delegated to a shallow, easily-bypassed check (`BaseCallFilter`) rather than to the strong consensus/membership proof that ISMP normally provides for the rest of the message.

### Impact Explanation
If the destination runtime's `BaseCallFilter` is permissive (the common default in many Substrate runtimes, e.g. `Everything` or an allow-list that is broader than intended for cross-chain-triggered calls), an attacker can craft `SubstrateCalldata.runtime_call` to invoke arbitrary dispatchables — including calls on other pallets never designed to be triggered by an unauthenticated cross-chain message (e.g. governance-adjacent calls, asset/currency operations, or calls in other bridge/escrow pallets) — bounded only by whatever origin `message.from` maps to. Because the entire `T::RuntimeCall` surface is reachable through SCALE-decoding an untrusted nested blob, this qualifies as "unauthorized app action": a message that should only move/mint tokens can also drive arbitrary runtime dispatch as a chosen account, which is a materially larger authority hand-off than the token-transfer feature nominally grants.

### Likelihood Explanation
High reachability: any relayer/token bridger holding tokens on a connected chain can trigger this path by calling the standard `send` function with a nonzero `call_data`, requiring no special privileges — only a legitimate ISMP delivery of a `PostRequest` that already passes proof verification for an unrelated (token-transfer) purpose. [8](#0-7)  The severity of what can be dispatched depends entirely on the specific runtime's `BaseCallFilter` configuration, which is not something verifiable from this repository's pallet code alone — this is the primary uncertainty in this analysis, since I could not fully confirm from the available Solidity/runtime configuration whether `message.from` is strictly bound to `msg.sender` on the EVM side, or whether any production runtime wiring this pallet uses a restrictive `BaseCallFilter` for this purpose.

### Recommendation
- Do not decode untrusted cross-chain bytes directly into `T::RuntimeCall`. Restrict the calldata-execution feature to an explicit allow-list of dispatchables intended for cross-chain triggering, separate from and stricter than the runtime's general `BaseCallFilter`.
- Require a signature (proving possession of the destination account's key) unconditionally before dispatching any decoded `RuntimeCall`, rather than allowing an unsigned path keyed only off `message.from`.
- Bind the decoded call's authorization explicitly to the value proven by the ISMP proof (e.g., only allow calls whose origin matches the escrowed/minted beneficiary and that are cryptographically signed for this specific request/nonce/commitment) rather than relying on an EVM-supplied byte field.

### Proof of Concept
Conceptual PoC (limited by the fact that the EVM-side `from` binding could not be fully verified from the indexed contract source in this session):
1. Attacker registers/holds any amount of a token bridged via `pallet-hyper-fungible-token` between an EVM chain and a Substrate chain.
2. Attacker calls `HyperFungibleToken.send(...)` on the EVM chain with `call_data` set to SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <SCALE bytes of a sensitive RuntimeCall> }`.
3. A relayer delivers the resulting ISMP `PostRequest` with a valid state proof to the destination chain; `on_accept` runs, decodes `SubstrateCalldata`, decodes `runtime_call` into `T::RuntimeCall`, checks only `BaseCallFilter`, and dispatches it with `RawOrigin::Signed(EvmToSubstrate::convert(message.from))`. [9](#0-8) 
4. If the target runtime's `BaseCallFilter` permits the chosen call, it executes without the destination account ever signing an extrinsic for it.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-59)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-200)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

			let origin = if let Some(signature) = substrate_data.signature {
				let multi_signature = MultiSignature::decode(&mut &*signature)
					.map_err(HftError::SignatureDecodeError)?;

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
					MultiSignature::Eth(_) => Err(HftError::EthSignatureUnsupported)?,
				};

				beneficiary.clone()
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

**File:** docs/content/developers/polkadot/hyper-fungible-token.mdx (L185-215)
```text
## Cross-Chain Message Format

The pallet encodes messages using the same ABI format as the Solidity contracts:

```solidity
struct Message {
    bytes from;    // original sender (for timeout refunds)
    bytes to;      // recipient on destination chain
    uint256 amount;
    bytes data;    // optional calldata
}
```

This ensures full compatibility between `pallet-hyper-fungible-token`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` on any chain.

---

## Calldata Execution

The `call_data` field in `SendParams` allows executing arbitrary runtime calls on the destination substrate chain after the tokens are transferred. The calldata is SCALE-encoded as:

```rust lineNumbers
pub struct SubstrateCalldata {
    /// Optional SCALE-encoded MultiSignature of (account_nonce, runtime_call)
    pub signature: Option<Vec<u8>>,
    /// SCALE-encoded runtime call to execute
    pub runtime_call: Vec<u8>,
}
```

If a signature is provided, it is verified against the beneficiary's account nonce and the runtime call before dispatch. Supported signature types: Ed25519, Sr25519, ECDSA. The account nonce is incremented after dispatch to prevent replay.
```
