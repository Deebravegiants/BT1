Found a concrete reachable out-of-bounds panic analog.

### Title
Unchecked slice-index underflow/panic on attacker-controlled `message.from` in `HyperFungibleToken::on_accept` - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` (the ISMP module handler for incoming HFT `PostRequest`s) decodes an ABI-encoded `Message` whose `from` field is an arbitrary-length `bytes` value fully controlled by the source-chain sender (the EVM `HyperFungibleToken` contract or any peer able to dispatch to this module once `ContractToAsset` authenticates the source). When the message carries optional `data` with no signature (`substrate_data.signature == None`) and `source.is_evm()` is true, the code computes `&from_bytes[from_bytes.len() - 20..]` without checking that `from_bytes.len() >= 20`.

### Finding Description [1](#0-0) 

- `message.from` is decoded via `Message::abi_decode(&body)` from arbitrary Solidity ABI bytes at line 59 — its length is not validated anywhere before this point (unlike `message.to`, which is length-checked against 20/32 at lines 65-71).
- If `from_bytes.len() < 20`, the subtraction `from_bytes.len() - 20` underflows a `usize`. In a `no_std` runtime/WASM context, this is not guarded by Rust's debug-mode overflow checks the way host-side code is; depending on build profile this either panics immediately (trap) on the subtraction, or wraps to a huge value and then panics on the out-of-bounds slice index. Either way, the pallet's `on_accept` unwinds into a runtime panic reachable directly from `handle_incoming_message`'s dispatch of an unsigned/relayed cross-chain message.
- Contrast this with the `else` branch (non-EVM source) at line 183, `account.copy_from_slice(from_bytes)`, which will also panic if `from_bytes.len() != 32` — the same missing-length-validation pattern exists there too.
- This is precisely the bug class in the external report (out-of-bounds memory access from crafted/adversarial input reaching decode/processing logic without bounds checks) and mirrors the exact pattern the codebase has already patched elsewhere (e.g. `StateMachine::from_str`'s `copy_from_slice` fix in `modules/ismp/core/src/host.rs:470-489`, and the `serde` `as_utf8_string` fix in `modules/utils/serde/src/lib.rs:529-554`, both of which explicitly call out that unchecked `copy_from_slice`/slicing on untrusted input panics and takes down a runtime worker).

### Impact Explanation
A relayer delivering an incoming HFT post-request (or the token-bridge contract encoding a malformed `from` field) can panic the runtime's message-dispatch path for this pallet. In a Substrate/FRAME `no_std` runtime, an unhandled panic inside extrinsic/dispatch execution triggers a WASM trap, which aborts block execution for that transaction — at minimum causing that request to be permanently stuck/unprocessable (denial of delivery for that specific message), and depending on how `handle_incoming_message` and the outer executive handle the trap, this can propagate to a full node crash or block-production failure for the message-processing path. This satisfies the "route unable to deliver messages" / freezing criteria in the validation section, since a legitimately-formed-looking but malformed cross-chain token message can be constructed by anyone who can get a `PostRequest` accepted from a registered source contract (an unprivileged token bridger/relayer path).

### Likelihood Explanation
Reaching this code requires: (1) `ContractToAsset::<T>::get(source, &from)` to resolve — i.e., the message must appear to originate from a registered bridge contract address, which is a source-chain contract identity check, not a value/length check on `message.from`; (2) `message.data` non-empty; (3) no `signature` present in `SubstrateCalldata`; (4) `source.is_evm()`. All of these are attacker-controllable by whoever can get a message dispatched with that `to`/`from` pairing (e.g., a malicious or buggy peer contract, or a relayer forging calldata if the source-side authentication is weaker than assumed). This is a moderate-likelihood, straightforward-to-trigger panic once a request is accepted by the router as originating from the registered contract — it does not require breaking any cryptography.

### Recommendation
Validate `from_bytes.len()` before both slicing paths, mirroring the existing check already applied to `message.to` at lines 65-71:
- For the EVM branch, require `from_bytes.len() >= 20` (or `== 20`) before slicing the last 20 bytes; return a typed error (e.g., a new `HftError::InvalidSenderLength(usize)`) otherwise.
- For the non-EVM branch, require `from_bytes.len() == 32` before `copy_from_slice`, returning the same style of typed error otherwise.

### Proof of Concept
1. Register a valid EVM source contract/asset mapping via `ContractToAsset` so a `PostRequest` from that `(source, from)` pair authenticates.
2. Craft an ABI-encoded `Message { from: <bytes shorter than 20>, to: <valid 20/32-byte>, amount: <any>, data: <SubstrateCalldata with signature: None, runtime_call: <any valid call>> }`.
3. Deliver this as an incoming `PostRequest` to the pallet's `on_accept` (via the normal ISMP dispatch/handler path, e.g. `handle_incoming_message`).
4. Execution reaches `modules/pallets/hyper-fungible-token/src/module.rs:177-181`, `from_bytes.len() - 20` underflows and the subsequent slice indexing panics, aborting execution of that message/extrinsic.

Note: I could not fully verify from the indexed code alone whether an outer `catch_unwind`/panic-handler wraps `on_accept` calls in this runtime (some Substrate runtimes use `frame_support`'s dispatch machinery, which does not generally catch panics from pallet logic — panics become WASM traps). Confirming the exact blast radius (single-tx revert vs. block-halting trap) would require checking the calling context in `pallet-ismp`'s `handle_incoming_message` and the runtime's panic-handling configuration, which is outside what the indexed snippets show with certainty.

### Citations

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
