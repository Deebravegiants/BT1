### Title
Missing length check on `message.from` before fixed-size slice causes a panic in `HftPallet::on_accept` — ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`Pallet::on_accept` in the hyper-fungible-token pallet's `IsmpModule` implementation decodes an attacker-controlled ABI-encoded `Message` and, when optional calldata is present with no signature, computes `from_bytes.len() - 20` on `message.from` and slices with it — without first checking that `from_bytes.len() >= 20`. This mirrors the reported OVS bug class: a fixed-size header/field is read off attacker-supplied data without verifying the data is long enough, leading to an unconditional panic on malformed input.

### Finding Description
`on_accept` decodes the incoming ISMP `PostRequest` body into a `Message` via ABI decoding: [1](#0-0) 

`message.from` is an ABI `bytes` field fully controlled by whatever EVM contract dispatches the cross-chain transfer (mapped as a trusted source contract via `ContractToAsset`, but the *content* of the message body, including `from`'s length, is not otherwise validated). Note that `message.to` (the recipient) *is* length-checked for exactly 20 or 32 bytes with an explicit error path: [2](#0-1) 

But when the message carries optional calldata (`message.data` non-empty) and no signature is supplied, the fallback "sender from EVM" branch reads a fixed 20-byte tail off `message.from` without any equivalent length check: [3](#0-2) 

If `from_bytes.len() < 20`, the subtraction `from_bytes.len() - 20` underflows `usize`, and the subsequent slice `&from_bytes[from_bytes.len() - 20..]` panics (either via an overflow-check panic on the subtraction itself, or via an out-of-bounds slice index once the underflowed value is used as an index) — exactly the same bug class as `key_extract()` unconditionally pulling `2 * ETH_ALEN` bytes without checking `skb` has enough linear data first.

### Impact Explanation
This code path executes inside `pallet-ismp`'s message-handling extrinsic (`handle_unsigned`/`handle` → module dispatch → `IsmpModule::on_accept`), which is executed deterministically by every validator/collator processing the block. An unhandled Rust panic here is not caught as a `Result::Err` — it traps WASM execution. Since the malformed message is embeddable in a normal relayed ISMP POST request from any registered EVM source contract (an unprivileged relayer/dispatcher can trigger a transfer with attacker-chosen calldata), a hostile actor can craft a message that every node processing the block must also attempt to execute, and every one of them panics the same way. This can stall inclusion/execution of that block for the pallet's route (or brick the extrinsic queue for this app), matching the "route unable to deliver messages" acceptance criterion — it is a token-bridge mint/transfer delivery path reachable from a single relayed request.

### Likelihood Explanation
High: the only precondition is that `message.data` is non-empty and no `signature` field is set in the decoded `SubstrateCalldata` — both of which are fields the attacker fully controls when constructing the source-chain ABI-encoded message; `message.from` is also attacker-controlled bytes length. No privileged role is required; only a normal cross-chain POST dispatched from a contract already mapped in `ContractToAsset` for some asset (a routine, non-privileged bridging operation) is needed to reach this code.

### Recommendation
Add an explicit length check on `message.from` before the arithmetic/slice, mirroring the existing check already done for `message.to`:
```rust
let from_bytes = message.from.as_ref();
if source.is_evm() {
    if from_bytes.len() < 20 {
        Err(HftError::InvalidSenderLength(from_bytes.len()))?;
    }
    T::EvmToSubstrate::convert(H160::from_slice(&from_bytes[from_bytes.len() - 20..]))
} else {
    if from_bytes.len() != 32 {
        Err(HftError::InvalidSenderLength(from_bytes.len()))?;
    }
    ...
}
```
Return a decode/validation error instead of panicking, so malformed messages are rejected gracefully rather than trapping runtime execution.

### Proof of Concept
1. Register a source EVM contract for some asset via `ContractToAsset`.
2. From that contract, dispatch a POST request whose ABI-encoded `Message` body has: `to` = valid 20-byte address, `amount` = any value, `data` = non-empty bytes decodable as `SubstrateCalldata` with `signature = None` and any `runtime_call`, and `from` = a `bytes` value shorter than 20 bytes (e.g., empty bytes).
3. Relay this request through pallet-ismp on the destination Hyperbridge-connected chain; `on_accept` is invoked with `source.is_evm() == true`.
4. Execution reaches `from_bytes.len() - 20` with `from_bytes.len() == 0`, underflowing and panicking (or slicing out of bounds), trapping the WASM runtime during that block's execution instead of returning a decode error.

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
