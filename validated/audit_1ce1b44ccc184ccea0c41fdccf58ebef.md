### Title
Unvalidated `message.from` Length Causes Runtime Panic (Denial of Service) in HyperFungibleToken `on_accept` - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`Pallet::on_accept` in the `hyper-fungible-token` pallet processes attacker-influenced ABI-decoded fields from a cross-chain `PostRequest` body without validating their length before using them in operations that panic on malformed input (`slice[len-20..]` underflow/out-of-bounds and `copy_from_slice` length mismatch). This is directly analogous to CVE-2021-32282's class of bug: missing input validation before a low-level operation leads to an unrecoverable crash (there, a NULL dereference in a parser; here, an index/length panic in message decoding) that a completely unprivileged party can trigger, causing Denial of Service.

### Finding Description
`on_accept` is invoked when `pallet-ismp` delivers a verified `PostRequest` to this application module — reachable by any unprivileged relayer via the permissionless `handle_unsigned` extrinsic [1](#0-0) , provided the request carries a valid consensus/state proof for its stated source chain.

Inside `on_accept`, the pallet ABI-decodes an application-level `Message` from the request `body` [2](#0-1) . Unlike the `to` field, which is explicitly length-checked (32 or 20 bytes, else a typed error) [3](#0-2) , the `from` field used for the optional-calldata authentication path has no such guard:

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
``` [4](#0-3) 

Two independent panic paths exist here, both reachable from an unbounded-length `bytes` field decoded straight from attacker-supplied `message.data`/`message.from` payloads:
1. **EVM branch:** if `from_bytes.len() < 20`, the subtraction `from_bytes.len() - 20` underflows a `usize`. On a debug/overflow-checked build this panics immediately with an arithmetic-overflow trap; on a wrapping build, the huge wrapped index makes the subsequent slice `&from_bytes[huge..]` panic with an out-of-bounds index — either way execution aborts with a Rust panic.
2. **Non-EVM branch:** `copy_from_slice` panics whenever `from_bytes.len() != 32` — the exact same "decode fixed-size buffer without checking length first" pattern that this codebase's own regression tests document as a previously-fixed, RPC-facing crash class elsewhere (`as_utf8_string`) [5](#0-4) ; this instance was evidently missed in the token-bridge module.

This code path is only reached when `substrate_data.signature` is `None` and `message.data` is non-empty, i.e. when the cross-chain transfer carries optional calldata to be executed as the unsigned-origin account rather than a self-signed one [6](#0-5) , [7](#0-6) .

A panic raised during runtime extrinsic execution (as opposed to a `DispatchError`/`Result::Err`) is not caught by `pallet-ismp`'s dispatch machinery the way `HftError` variants are — it unwinds through Wasm execution during block authoring/import. Since every validator/collator importing or authoring the block executes the same message deterministically, this can abort block production/import for all nodes processing that block, which is a stronger DoS than a single failed extrinsic.

### Impact Explanation
Any unprivileged relayer who can get a `PostRequest` with a crafted `body` proven against a legitimate (but attacker-influenced, e.g. self-controlled dispatch on an EVM chain the attacker can call) source-chain state can trigger a Rust panic during `on_accept` execution on Hyperbridge. Because this executes inside deterministic runtime/block-execution code reachable by any relayer submitting `handle_unsigned`, it can crash/halt block execution for validating nodes processing that message — a "route unable to deliver messages" / liveness-DoS impact, which the scope explicitly treats as valid (Medium-severity class, matching the CVE's DoS characterization).

### Likelihood Explanation
Likelihood is Medium-High for an attacker who has (or can cheaply acquire) any pre-registered `ContractToAsset` mapping for a source EVM chain (i.e., an attacker that operates or controls the mapped gateway contract's dispatch call, or can otherwise get a message with attacker-chosen `body` bytes delivered as a `PostRequest` from that `(source, from)` pair). Since `body` is ABI-decoded application data independent of ISMP-level routing fields, and the pallet does not bound `message.from`'s length before use, no special privilege beyond submitting a normally-provable cross-chain message is required.

### Recommendation
Validate `from_bytes.len()` before use, mirroring the existing `to_bytes` handling:
- For the EVM branch, require `from_bytes.len() == 20` (or explicitly handle longer inputs by taking the last 20 bytes only via `checked_sub`), returning a typed `HftError` on mismatch instead of slicing.
- For the non-EVM branch, require `from_bytes.len() == 32` before `copy_from_slice`, returning a typed error otherwise.
Add regression tests analogous to the existing `as_utf8_string_rejects_non_four_byte_input` / `empty_hp_prefix_returns_error_not_panic` tests already present in this codebase for other decode-time panics.

### Proof of Concept
1. Craft an ABI-encoded HFT `Message` with `to` = a valid 20/32-byte recipient, `amount` a small nonzero value, and `data` = a non-empty `SubstrateCalldata` with `signature = None` and any decodable `runtime_call`.
2. Set the embedded `message.from` field to a short byte string (e.g. 3 bytes) — this is a sub-field of `body`, distinct from and independent of the top-level `PostRequest.from`/`source` used only for the `ContractToAsset` lookup.
3. Get this `PostRequest` legitimately proven (e.g., by dispatching it from a governance-mapped gateway contract you control, or any contract mapped in `ContractToAsset` for the target `local_asset_id`) and relay it via `pallet_ismp::Call::handle_unsigned`.
4. During `on_accept` execution, once `source.is_evm()` evaluates true and `substrate_data.signature` is `None`, `from_bytes.len() - 20` underflows (`3 - 20`), triggering an arithmetic-overflow/slice-index panic and aborting execution of the extrinsic/block.

**Note on verification limits:** I was not able to fully confirm from the indexed contents whether the EVM-side gateway contract (`HyperFungibleToken.sol`) always forces `message.from` to be exactly 20 bytes (e.g., `abi.encodePacked(msg.sender)`) or allows a caller-supplied value of arbitrary length; the index did not return the relevant contract body for `HyperFungibleToken.sol`. If the source-chain contract always emits exactly 20 (or 32) bytes for `from`, exploitability requires either a bug/compromise on that contract or an attacker deploying/controlling their own mapped gateway contract that emits a malformed `from`. A Devin session with full repository access would be needed to inspect `sdk/packages/core/contracts/apps/HyperFungibleToken.sol` and confirm the exact encoding contract-side.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-59)
```rust
		// Decode the Message
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-124)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

			let origin = if let Some(signature) = substrate_data.signature {
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

**File:** modules/utils/serde/src/lib.rs (L529-533)
```rust
	// `as_utf8_string` deserializes into a fixed `[u8; 4]`. It used to `copy_from_slice`
	// straight from the input, which panics on any length mismatch — and it runs on
	// untrusted RPC input (`consensus_state_id`), so the panic aborted the node's `rpc`
	// worker thread and took the process down. Wrong lengths must be serde errors.
	#[test]
```
