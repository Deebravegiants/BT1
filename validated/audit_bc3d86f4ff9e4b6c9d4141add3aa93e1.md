This is a genuine finding. In `modules/pallets/hyper-fungible-token/src/module.rs`, the `on_accept` handler (lines 176–186) computes `message.from.as_ref()` and, when `source.is_evm()`, indexes `&from_bytes[from_bytes.len() - 20..]` without first checking that `from_bytes.len() >= 20`. Contrast this with the sibling code path at lines 62–71 (for `message.to`) and lines 224–232 (`on_timeout`, for `message.from`), both of which explicitly validate the length is either 20 or 32 bytes and return a typed `HftError` otherwise. The `message.from` field used at line 177 comes from ABI-decoding the attacker-controlled `body` of an incoming cross-chain POST request (`Message::abi_decode(&body)` at line 59) — this is fully attacker-controlled since `message.from` is an arbitrary `bytes` field in the ABI-encoded message, not validated against any known length before this branch is reached.

### Title
Unchecked length subtraction on attacker-controlled `message.from` causes panic/OOB slice in `HyperFungibleToken::on_accept` - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`on_accept` decodes an ABI-encoded `Message` from an untrusted cross-chain POST request body. When that message carries optional calldata (`message.data`) without an embedded signature, the code derives the dispatch origin from `message.from` by computing `from_bytes.len() - 20` and slicing at that offset — with no length check first. [1](#0-0) 

### Finding Description
`message.from` is an arbitrary-length `bytes` field decoded from the request body via `Message::abi_decode(&body)` [2](#0-1) . Nothing constrains its length before it reaches the `source.is_evm()` branch. If `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows `usize`: in a debug/checked build this panics with subtract-overflow; in a release build it wraps to a huge value, producing an out-of-bounds slice index that panics the runtime with an unchecked slice-range error. Either way, this is analogous to CVE-2020-28598's root cause — an out-of-bounds memory access triggered by indexing into a buffer using an attacker-controlled length/offset derived from untrusted file/message data without a prior bounds check — except here the "file" is the cross-chain message body and the "buffer" is `from_bytes`.

This is inconsistent with the rest of the same function: the `to_bytes` conversion just above (lines 62–71) and the equivalent `from_bytes` handling in `on_timeout` (lines 224–232) both explicitly match on `len() == 32` / `len() == 20` and return `HftError::InvalidRecipientLength`/similar otherwise, showing the intended, safe pattern that this branch fails to apply. [3](#0-2) [4](#0-3) 

### Impact Explanation
A relayer delivering a maliciously crafted cross-chain POST request (any source chain registered as an EVM source contract in `ContractToAsset`) can craft `message.from` to be shorter than 20 bytes while including non-empty `message.data` with `substrate_data.signature == None`. This deterministically panics the runtime's `on_accept` dispatch execution, halting/reverting message processing (denial of service on message delivery / the whole extrinsic including the token mint that already occurred earlier in the function may be rolled back depending on transactional semantics, and future messages relying on the same block execution can also be disrupted). At minimum this is a permanent inability to deliver certain classes of messages/route disruption; depending on how `on_accept` panics interact with the pallet-ismp dispatch transactional wrapper, it may also cause state inconsistency around the just-completed mint/transfer of `amount` to `beneficiary`.

### Likelihood Explanation
High. This is reachable through the standard "single relayed message" path (any relayer submitting a POST request to this HFT module) using a self-authored ABI-encoded `Message` payload from an authorized/allow-listed source contract address (`ContractToAsset` lookup keyed by `(source, from)` uses `from`'s exact bytes as configured — an attacker deploying/controlling the source-side contract at that mapped address, or replaying an existing valid `from`, then crafting the `data`/calldata sub-message independently, still reaches this code since `message.from` inside the ABI body is a separate field from the top-level ISMP `from`). No special privileges beyond being able to dispatch a cross-chain message from a registered source are required.

### Recommendation
Add the same explicit length check used elsewhere in this file before slicing: validate `from_bytes.len() == 20` (or `== 32`) for the EVM/substrate branches respectively and return a typed error (e.g., `HftError::InvalidSenderLength`) otherwise, mirroring the pattern already used for `to_bytes` (lines 62–71) and in `on_timeout` (lines 224–232).

### Proof of Concept
1. Register a source EVM contract address `S` for state machine `source` in `ContractToAsset` (as required for `on_accept` to proceed past the initial lookup).
2. Craft a POST request with `from = S`, `body` = ABI-encoded `Message` where:
   - `to` = valid 20 or 32 byte recipient,
   - `amount` = any valid amount,
   - `data` = ABI-encoded `SubstrateCalldata { signature: None, runtime_call: <any allowed call> }`,
   - the inner `message.from` field (encoded within `data`'s originating `Message`, distinct from the outer ISMP `from`) is set to fewer than 20 bytes, e.g. an empty byte string.
3. Deliver this request through the standard ISMP relaying path to the HFT pallet.
4. Execution reaches line 180: `from_bytes.len() - 20` underflows since `from_bytes.len() == 0`, causing a panic / out-of-bounds slice access in `on_accept`. [1](#0-0)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-59)
```rust
		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L62-71)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L220-230)
```rust
			Request::Post(PostRequest { body, to, dest, .. }) => {
				let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

				// Refund the original sender
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
```
