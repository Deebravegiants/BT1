### Title
Unbounded `message.from` bytes cause a panic/DoS in `HyperFungibleToken::on_accept` when executing cross-chain calldata - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` in the `hyper-fungible-token` pallet decodes an ABI-encoded `Message` from an incoming ISMP `PostRequest` body, and when `message.data` carries `SubstrateCalldata` with no `signature`, it derives the calling account directly from `message.from` without validating its length before slicing/copying it into a fixed-size buffer.

### Finding Description
In `on_accept`, after ABI-decoding the `Message` struct (whose `from` field is an arbitrary-length `bytes` under caller control per the Solidity mirror `struct Message { bytes from; bytes to; uint256 amount; bytes data; }`), the unsigned branch does: [1](#0-0) 

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

Note that `message.to` (the recipient) is validated with explicit length checks and an `Err(HftError::InvalidRecipientLength(...))` a few lines earlier [2](#0-1)  — but no equivalent check exists for `message.from`. If the source state machine is EVM and `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows (a subtract-with-overflow panic under overflow checks, or a huge wrapped index causing an out-of-bounds slice panic otherwise). If the source is non-EVM, `account.copy_from_slice(from_bytes)` panics unless `from_bytes.len()` is exactly 32.

This is the same bug class as CVE-2021-4186 (a decoder that indexes/copies attacker-controlled bytes into a fixed-size structure without a length check, causing a crash): here the "packet" is the ABI-encoded ISMP message body, and the "dissector" is `on_accept`.

### Impact Explanation
The `from` field is inside the abi-encoded `Message.data` payload, which is chosen entirely by whoever calls the source-chain `HyperFungibleToken`/`WrappedHyperFungibleToken` contract to initiate a transfer — an ordinary unprivileged user/relayer, not the pegged bridge contract itself, since `data` is a free-form calldata blob for the destination-chain call, only the top-level `from`/`source` of the `PostRequest` (checked via `ContractToAsset`) is trusted, not the nested `Message.from` bytes embedded in the payload. `on_accept` runs as part of ISMP message execution triggered by `handle_unsigned`/`execute`, which is dispatched as an unsigned extrinsic reachable by any relayer submitting a delivery message with a valid state/consensus proof for an otherwise legitimate transfer. A crafted `Message.from` of the wrong length causes a Rust panic during dispatch, which — depending on how the runtime wraps pallet execution — can abort block execution or crash the node process, denying service to the chain's message-handling path (a permanent halt of the reachable route for delivering HFT messages until the code is patched).

### Likelihood Explanation
High: the attacker only needs to call the source-chain HFT/WrappedHFT contract with a token transfer whose optional calldata sets `signature = None` and `runtime_call` non-empty (so the unsigned branch executes) and picks `Message.from` with an invalid byte length (e.g., 0 bytes for EVM source, or any length other than 32 for non-EVM source). No proof forgery or race condition is needed beyond the normal relaying flow; the relayer only needs to deliver a message whose proof is valid for content the attacker fully controls (the calldata bytes), just as any legitimate HFT transfer would be relayed.

### Recommendation
Validate `from_bytes.len()` before use, mirroring the existing `message.to` handling: for EVM sources require exactly 20 bytes (return `HftError::InvalidRecipientLength`/a new `InvalidFromLength` error otherwise) and for non-EVM sources require exactly 32 bytes, replacing the unchecked slice/`copy_from_slice` with checked `try_into()`/explicit length comparisons that return a typed error instead of panicking.

### Proof of Concept
1. On the source EVM chain, call `HyperFungibleToken.send(...)` (or the underlying dispatch path) targeting the substrate hyper-fungible-token pallet, setting the optional `data` field to an ABI-encoded `SubstrateCalldata { signature: None, runtime_call: <any non-empty bytes> }`, and set the outer `Message.from` to a byte string of length 0 (or any length ≠ 20 while `source.is_evm()` is true).
2. Relay the resulting `PostRequest` to the destination substrate chain with a valid consensus/state proof (a normal, honestly-relayed message — no proof forgery required).
3. When `pallet_ismp::execute` dispatches to `HyperFungibleToken::on_accept`, execution reaches `let from_bytes = message.from.as_ref();` and then `&from_bytes[from_bytes.len() - 20..]`, which underflows/panics because `from_bytes.len() < 20`, crashing the extrinsic execution.

Note: I was unable to fully trace how a panic inside `on_accept` is caught (or not) by the calling `pallet_ismp`/router dispatch machinery (e.g., whether `Self::execute` wraps module calls in `catch_unwind` or similar), so the exact blast radius (extrinsic revert vs. node/process crash) could not be confirmed with certainty from the indexed code — a Devin session with full repository access would be needed to trace `ismp::handlers`/router dispatch and confirm whether this panic is contained or propagates to a full node crash.

### Citations

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
