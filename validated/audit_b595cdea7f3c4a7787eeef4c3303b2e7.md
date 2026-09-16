I found a concrete out-of-bounds-write analog to the ap_escape_quotes() bug class in `modules/pallets/hyper-fungible-token/src/module.rs`.

### Title
Panic / DoS via unchecked fixed-size buffer write on attacker-controlled `message.from` in HFT `on_accept` calldata path - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
The ALPINE-CVE-2021-39275 bug class is: a length-unchecked write into a fixed-size buffer driven by attacker-controlled data. `pallets/hyper-fungible-token`'s `on_accept` handler (reached by any relayed cross-chain `PostRequest` that any unprivileged relayer can deliver via `HandlerV2`/`pallet-ismp`) contains the same pattern: it slices and `copy_from_slice`s into a fixed `[0u8; 32]` / uses `H160::from_slice` on attacker-controlled `message.from` bytes without validating the length first, unlike the sibling `to_bytes` handling a few lines above and the `on_timeout` handler further down in the same file, both of which validate length (`==32`/`==20`) before writing.

### Finding Description
In `on_accept` at [1](#0-0) , when `message.data` carries a `SubstrateCalldata` with no `signature`, the code derives the dispatch origin straight from `message.from`:

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

`message.from` is decoded from the ABI-encoded `body` of an ISMP `PostRequest` (`Message::abi_decode(&body)` at line 59), which is fully attacker-controlled — a `bytes` field in a Solidity struct can be any length. Two failure modes exist:
- If `source.is_evm()` and `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows (`usize` subtraction), causing a panic (in debug) or an out-of-range slice index panic in release (the subsequent slicing still panics on an out-of-bounds/negative-length range).
- If `!source.is_evm()` and `from_bytes.len() != 32`, `copy_from_slice` panics on a length mismatch (this is exactly the same class of bug the codebase's own regression tests elsewhere explicitly guard against, e.g. `modules/ismp/core/src/host.rs:470-489` and `modules/utils/serde/src/lib.rs:529-564`, which document that unchecked `copy_from_slice` on untrusted input is a known, previously-fixed footgun in this repo).

Notably, the exact same file already validates length correctly in two other places handling the analogous `to`/`from` fields:
- `to_bytes` in `on_accept`, lines [2](#0-1) , checks `len() == 32` / `len() == 20` before any write.
- `from_bytes` in `on_timeout`, lines [3](#0-2) , also checks length before `copy_from_slice`.

This shows the unchecked path at lines 177-186 is an inconsistency/regression relative to the pattern the rest of the module follows, not an intentional design choice.

### Impact Explanation
`on_accept` is invoked from `IsmpModule::on_accept` when a `PostRequest` destined for the HFT pallet's contract is delivered by `pallet-ismp`'s `handle_unsigned`/message-handling path — reachable by any relayer submitting a relayed cross-chain message with a valid consensus/membership proof (the proof only needs to be valid for the request's existence, not for its `body` contents, since `body` is application payload chosen entirely by the sending contract/account on the source chain). A malicious or compromised sender on the source EVM chain (anyone permitted to call the paired source-side HFT contract with an arbitrary `from`-equivalent payload) can craft a `Message.from` of length 0, 1, or any value other than 20/32 to trigger a panic inside pallet-ismp's message dispatch. In a Substrate runtime, an unhandled panic inside dispatch typically aborts the transaction via `frame_support`'s panic-to-error boundary for signed extrinsics, but for `handle_unsigned`/off-chain-worker-driven or block-execution paths a panic during STF execution can halt block production or crash the node process — the same class of impact the codebase's own comments document for `copy_from_slice`-on-untrusted-input bugs ("a wasm trap reachable from untrusted input ... took the process down" — see `modules/utils/serde/src/lib.rs:531-532` and `modules/ismp/core/src/host.rs:472-474`). This is a message-delivery-halting/DoS condition on a path reachable from a single relayed message, satisfying "a route unable to deliver messages" / permanent disruption criteria.

### Likelihood Explanation
High. Nothing about the transport encoding (`Message::abi_decode`) constrains `from` to 20 or 32 bytes — it is a Solidity `bytes` ABI field, so any length is a valid encoding. Triggering the bug only requires a relayer to deliver a `PostRequest` whose `body`, once ABI-decoded, has a non-standard-length `from` and a `data` payload containing a `SubstrateCalldata` with `signature: None`. No privileged role, no forged proof, and no special network conditions are needed — only a normal message-delivery flow with an attacker-influenced payload field.

### Recommendation
Mirror the validation already used for `to_bytes` (lines 63-71) and for `from_bytes` in `on_timeout` (lines 224-230): explicitly check `from_bytes.len() == 20` or `== 32` (as appropriate for the `source.is_evm()` branch) and return a typed `HftError` (e.g. `InvalidRecipientLength`/a new `InvalidSenderLength`) instead of slicing/copying unconditionally.

### Proof of Concept
1. On the source EVM chain, from any account, call the paired HFT contract's dispatch function with a `Message` whose ABI-encoded `body` contains a `from` field of, e.g., 5 bytes (or `0` bytes), and a non-empty `data` field encoding a `SubstrateCalldata { signature: None, runtime_call: <any allowed call> }`.
2. Have any relayer deliver this `PostRequest` to the destination Substrate chain through the normal `pallet-ismp` handling path (`handle_unsigned`/`Message::Request`), with a valid membership proof for the request's existence (the request's existence proof does not validate the semantic length of `from` inside `body`).
3. During `on_accept` execution, `from_bytes.len() - 20` underflows for the EVM-source branch (or `copy_from_slice` panics on the substrate-source branch), panicking inside dispatch of the ISMP message and halting normal processing of that block/extrinsic.

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L224-230)
```rust
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
```
