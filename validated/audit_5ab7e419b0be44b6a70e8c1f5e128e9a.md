### Title
Unchecked-length slice underflow panic in `hyper-fungible-token` on_accept unsigned-calldata path — (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::<T>::on_accept` (the ISMP module callback invoked for every inbound `PostRequest` delivered to the hyper-fungible-token bridge) reads the attacker-supplied `message.from` byte field and, when the calldata section carries no signature, computes `from_bytes.len() - 20` to slice out an EVM address without first checking that `from_bytes` is at least 20 bytes long [1](#0-0) . This is the same bug class as CVE-2017-8363: a decoder computes an offset/length from untrusted input and reads/copies past (or, here, "before") the buffer boundary because an implicit length invariant was assumed but never enforced.

### Finding Description
The `Message` ABI-decoded from the incoming `PostRequest.body` carries a `from` field of dynamic `bytes` type, entirely controlled by whoever constructs the message on the source chain [2](#0-1) . Elsewhere in the same function the code is careful to validate lengths before use — the `to` field is checked to be exactly 32 or 20 bytes before any indexing, with an explicit `InvalidRecipientLength` error otherwise [3](#0-2) , and the same discipline is applied to `from_bytes` in the `on_timeout` handler [4](#0-3) .

However, in the unsigned-calldata branch of `on_accept` (executed whenever `substrate_data.signature` is `None`, i.e. the optional runtime-call payload has no attached signature), the code does:
```rust
let from_bytes = message.from.as_ref();
if source.is_evm() {
    T::EvmToSubstrate::convert(H160::from_slice(
        &from_bytes[from_bytes.len() - 20..],
    ))
} else { ... }
```
with no length check on `from_bytes` at all [5](#0-4) . If an attacker crafts a source-chain message whose `from` field is shorter than 20 bytes, `from_bytes.len() - 20` underflows `usize`, and the subsequent range-index panics (either directly from the arithmetic underflow, or from the resulting massive/garbage range being sliced against a short buffer).

### Impact Explanation
`on_accept` runs inside pallet-ismp's `handle_request`/module-dispatch path for every delivered PostRequest — a panic here aborts the runtime's transaction-execution context. Because ISMP request delivery is processed inside a Substrate extrinsic (`handle_unsigned`/relayer-submitted proof), an unhandled panic during dispatch of a module callback halts block execution for that transaction and can be used to repeatedly disrupt processing of legitimate cross-chain messages routed through this pallet, i.e. a route unable to deliver messages once the crafted request is included and re-processed (requests are retried on failure paths in ISMP, which can turn a single malformed message into a durable denial-of-service against this application module).

### Likelihood Explanation
Reachable by any party able to get a `PostRequest` accepted for the `hyper-fungible-token` module and successfully relayed with a valid state/consensus proof — i.e., a normal token-bridge user/relayer path, not a privileged actor. The attacker only needs control over the encoded `message.from` bytes in the payload (dynamic bytes field, no on-chain length enforcement prior to this callback) and to route the message through a registered source contract/asset pair, and to supply a non-empty `message.data` with no `substrate_data.signature`. This does not require compromising the source contract's normal transfer logic — an attacker who can call the bridging entry point with a manually encoded payload (e.g. via a helper/relay contract, or directly if the source ABI permits specifying `from` as arbitrary bytes) can trigger it.

### Recommendation
Add the same explicit length check used for `to_bytes` and in `on_timeout` before slicing `from_bytes`, returning a typed error (e.g. `HftError::InvalidSenderLength`) for any length other than 20 (EVM) or 32 (Substrate), instead of performing unchecked arithmetic on `from_bytes.len()`.

### Proof of Concept
1. Register a source contract/asset mapping via `ContractToAsset` as usual.
2. Construct and relay a `PostRequest` to the `hyper-fungible-token` module whose ABI-encoded body decodes to a `Message` with:
   - `to`: a valid 20-byte address (to pass the earlier check),
   - `from`: fewer than 20 raw bytes (e.g. 1 byte),
   - `data`: a non-empty `SubstrateCalldata` with `signature = None`.
3. Delivered through the standard ISMP request-handling path, `on_accept` reaches the `else` branch at [5](#0-4) , computes `from_bytes.len() - 20` (underflow), and panics when slicing, aborting the extrinsic.

Note: I could not fully verify the exact Solidity-side encoding contract for the `Message.from` field (whether the trusted source contract always forces this to 20 bytes) due to index/documentation limits on the EVM source side; the Rust-side decoder has no independent enforcement, so if any path allows an attacker to influence the raw encoded bytes without going through that constraint, this bug is triggerable. This uncertainty should be resolved by reviewing the corresponding Solidity `Message` encoder used by the hyper-fungible-token source contracts.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L59-60)
```rust
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L63-71)
```rust
		let mut beneficiary_bytes = [0u8; 32];
		let to_bytes = message.to.as_ref();
		if to_bytes.len() == 32 {
			beneficiary_bytes.copy_from_slice(to_bytes);
		} else if to_bytes.len() == 20 {
			beneficiary_bytes[12..].copy_from_slice(to_bytes);
		} else {
			Err(HftError::InvalidRecipientLength(to_bytes.len()))?;
		}
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L224-232)
```rust
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
					Err(HftError::InvalidSenderLength(from_bytes.len()))?
				}
```
