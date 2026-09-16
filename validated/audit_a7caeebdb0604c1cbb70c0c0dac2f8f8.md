Confirmed: `Message.from` is an ABI `bytes` field of arbitrary attacker-controlled length (from `alloy_sol_macro::sol!` struct in `modules/pallets/hyper-fungible-token/src/types.rs:37-42`), fully controlled by whoever calls the source-chain `HyperFungibleToken` contract that gets relayed as an ISMP `PostRequest`. No length validation exists on `from` (unlike `to`, which is validated at `modules/pallets/hyper-fungible-token/src/module.rs:64-71`).

### Title
Out-of-bounds slice panic on attacker-controlled `Message.from` length in `HyperFungibleToken::on_accept` - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`on_accept` decodes an ABI `Message` whose `from` field is an unbounded, attacker-controlled `bytes` value [1](#0-0) . When optional calldata is executed without a signature, `from_bytes` is sliced/copied with no length check, causing an out-of-bounds panic analogous to the HDF5 heap-based buffer over-read (unvalidated length used to index/copy a buffer).

### Finding Description
In `on_accept`, when `message.data` is non-empty and `substrate_data.signature` is `None`, the origin account is derived directly from `message.from`: [2](#0-1) 

- For `source.is_evm()`: `from_bytes.len() - 20` is computed with no check that `from_bytes.len() >= 20`. If the relayed message sets `from` to fewer than 20 bytes (including the trivially valid empty `bytes` value), this `usize` subtraction underflows, producing either an "attempt to subtract with overflow" panic (debug) or, in release (wrapping), a huge index that makes `&from_bytes[huge..]` panic with an out-of-range slice index.
- For the non-EVM branch: `account.copy_from_slice(from_bytes)` requires `from_bytes.len() == 32` exactly; any other length (also unchecked) panics with "source slice length does not match destination slice length".

Unlike `message.to`, which is explicitly validated to be 20 or 32 bytes with a graceful `HftError::InvalidRecipientLength` otherwise (`module.rs:64-71`), `message.from` receives no equivalent validation before being consumed at line 180/184. The `from` field originates from the source-chain contract call parameters relayed via ISMP `PostRequest.body`, i.e., fully attacker-controlled data reaching `on_accept` through the standard, unprivileged relay path (`ContractToAsset` lookup only authenticates which asset/contract pair is registered, not the contents of `from`).

### Impact Explanation
A malicious (or malformed) sender on any registered EVM source chain can craft a token-transfer message with calldata (`message.data` non-empty), no signature, and a `from` field shorter than 20 bytes (EVM branch) or not exactly 32 bytes (substrate branch). Relaying this message through the standard ISMP delivery path triggers an unhandled panic inside `on_accept`, which executes as part of normal message-handling extrinsic execution. This aborts processing of the incoming request/extrinsic, causing a denial-of-service in message delivery — the underlying token mint/transfer that already occurred earlier in the same function (`module.rs:93-117`) is affected by the panic's transactional rollback behavior, and legitimate token transfers bundled with calldata can be forced to permanently fail, effectively freezing tokens that were meant to be delivered together with a call, or halting relayer processing of the queue depending on the pallet's transactional/panic-handling wrapper.

### Likelihood Explanation
High. This requires only a single crafted cross-chain message (any user able to call the registered source-chain contract, then relayed by any unprivileged relayer) — no governance or privileged role needed. The `from` value is fully attacker-controlled with no length precondition enforced anywhere before use.

### Recommendation
Validate `message.from`'s length exactly as `message.to` is validated before use — reject with a proper `HftError` (e.g., `InvalidSenderLength`) if it is not exactly 20 bytes (EVM) or 32 bytes (substrate), instead of performing an unchecked subtraction/slice and `copy_from_slice`.

### Proof of Concept
1. Attacker calls the registered `HyperFungibleToken` contract on the EVM source chain (or crafts the raw ISMP `PostRequest.body`) encoding `Message { from: b"" /* 0 bytes */, to: <valid 20 or 32 bytes>, amount: X, data: <non-empty SCALE SubstrateCalldata with signature = None> }`.
2. This request is relayed normally (no special privilege needed) and reaches `HyperFungibleToken::on_accept` on the destination chain via `modules/pallets/hyper-fungible-token/src/module.rs`.
3. Execution proceeds past the mint/transfer step, then enters the `!message.data.is_empty()` branch with `substrate_data.signature == None`.
4. At `module.rs:180`, `from_bytes.len() - 20` computes `0usize - 20`, causing a panic (or, if compiled with wrapping arithmetic, wraps to `usize::MAX - 19` and then `&from_bytes[huge..]` panics on out-of-range slicing).
5. The panic aborts the extrinsic/message handling, denying delivery of this (and potentially subsequent) messages. [2](#0-1) [3](#0-2) [1](#0-0)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L35-43)
```rust
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
