### Title
Out-of-bounds/panic in `on_accept` HFT calldata dispatch: unchecked length before slicing trailing 20 bytes of `message.from` - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`HyperFungibleToken::on_accept` decodes an ABI-encoded `Message` from an ISMP `PostRequest` body and, when the message carries optional calldata without an embedded signature, derives the dispatch `origin` from `message.from` by slicing its **trailing 20 bytes** — `&from_bytes[from_bytes.len() - 20..]` — with no check that `from_bytes.len() >= 20` first. Every other place in this same pallet that consumes an attacker/relayer-supplied address-like byte field (`to_bytes` a few lines above, and `from_bytes` in the sibling `on_timeout` handler) explicitly validates the length is 20 or 32 bytes and returns a typed error otherwise. This one call site is missing that check.

### Finding Description
In `on_accept`: [1](#0-0) 
`to_bytes` is validated (`== 32` or `== 20`, else `Err(HftError::InvalidRecipientLength)`).

Later, in the "no embedded signature" branch that determines the dispatch origin for the optional runtime call attached to the cross-chain message: [2](#0-1) 
```rust
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
```
Neither branch validates `from_bytes.len()` before use:
- If `source.is_evm()` and `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows `usize` (panics with overflow checks, or wraps to a huge index that panics on the subsequent out-of-bounds slice), causing a runtime panic.
- If `!source.is_evm()` and `from_bytes.len() != 32`, `copy_from_slice` panics on a length mismatch.

The sibling handler `on_timeout` reads the same conceptual field (`message.from`) and *does* validate it first: [3](#0-2) 
This shows the intended/expected pattern that the `on_accept` branch omits.

`message.from` is decoded straight out of the attacker/relayer-supplied ABI request body via `Message::abi_decode(&body)`: [4](#0-3) 
Its length is only constrained by the Solidity `bytes` ABI encoding, not by this pallet — the same class of bug as the JLSEC-2026-700 report: a fixed-size trailing read (there, 65 bytes of an SM2 public key; here, 20 bytes of an EVM address) performed without first checking the source buffer is at least that long.

### Impact Explanation
This is reachable via the standard ISMP dispatch path: any relayer that delivers a `PostRequest` from a registered source contract (`ContractToAsset::get(source, &from)` only gates on the *outer* IsmpModule `from`/`source`, not on the *inner* `message.from` field decoded from the body) triggers `on_accept`. As long as the request carries non-empty `message.data` with `SubstrateCalldata.signature == None` and the request originates from a state machine where `source.is_evm()` is true, the attacker fully controls `message.from`'s byte length inside the ABI-encoded body. Supplying `message.from` shorter than 20 bytes triggers an unhandled arithmetic-underflow/out-of-bounds panic in on-chain runtime code executing inside block execution (`on_accept` is called from pallet-ismp message handling), which is a Substrate runtime panic — i.e., halts/reverts the block's state transition for that message and, depending on the pallet-ismp execution context, can be a denial-of-service against message processing for this pallet. It does not enable unbacked mint or fund theft; it is High-severity denial-of-service consistent with CVSS 7.5 AV:N/AC:L/.../A:H of the analog report (no C, no I, but A:H).

### Likelihood Explanation
High likelihood: reaching `on_accept` requires only a legitimately-routed `PostRequest` from a contract already registered in `ContractToAsset` for some source EVM chain — a normal, expected message. The attacker needs to control only the ABI-encoded `message.from` bytes and `message.data`/`SubstrateCalldata` fields of the request body (no signature needed on this path), both of which are part of the request payload the relayer submits and are not independently validated for length before this slice operation.

### Recommendation
Add the same explicit length check used for `to_bytes` (lines 64-71) and for `on_timeout`'s `from_bytes` (lines 224-232) before deriving the dispatch origin in the no-signature branch of `on_accept`: require `from_bytes.len() == 20` (EVM) or `== 32` (Substrate), returning a typed `HftError` (e.g. reuse/extend `InvalidSenderLength`) otherwise, instead of performing the unchecked `from_bytes.len() - 20` slice.

### Proof of Concept
1. On the registered source EVM contract's counterpart, craft (or have a malicious/compromised relayer submit) a `PostRequest` whose ABI-encoded body decodes to a `Message` with:
   - `to`: valid 20-byte recipient (passes the `to_bytes` check),
   - `data`: non-empty, decoding to `SubstrateCalldata { signature: None, runtime_call: <any allowed call> }`,
   - `from`: a `bytes` field of length < 20 (e.g. empty or 5 bytes).
2. Deliver this request through the normal ISMP relay path to a chain running `pallet-hyper-fungible-token`, with `source` such that `source.is_evm()` is true.
3. `on_accept` proceeds through minting/transfer, reaches the no-signature branch, computes `from_bytes.len() - 20` which underflows, and the runtime panics while resolving the dispatch origin — before the runtime call filter or dispatch even executes.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-72)
```rust
		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

		// Convert recipient bytes to substrate AccountId
		// If 32 bytes: use directly. If 20 bytes: left-pad with zeros.
		let mut beneficiary_bytes = [0u8; 32];
		let to_bytes = message.to.as_ref();
		if to_bytes.len() == 32 {
			beneficiary_bytes.copy_from_slice(to_bytes);
		} else if to_bytes.len() == 20 {
			beneficiary_bytes[12..].copy_from_slice(to_bytes);
		} else {
			Err(HftError::InvalidRecipientLength(to_bytes.len()))?;
		}
		let beneficiary: T::AccountId = beneficiary_bytes.into();
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L176-186)
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
