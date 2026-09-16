## Finding: Missing length validation before fixed-size buffer copy in `HyperFungibleToken::on_accept`

### Title
Panic via unvalidated `message.from` length in `pallet-hyper-fungible-token` `on_accept` calldata-origin resolution - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
The libtiff `_TIFFmemcpy` bug class is: a fixed-size copy is performed using a length taken from untrusted input without validating that the length matches the destination buffer, causing an out-of-bounds read/write. The Hyperbridge analog is in the `IsmpModule::on_accept` handler of `pallet-hyper-fungible-token`, where the ABI-decoded, cross-chain-attacker-influenced `message.from` bytes are sliced and `copy_from_slice`d into fixed-size arrays without any length check, unlike the sibling `message.to` handling three lines earlier which explicitly validates length.

### Finding Description
In `on_accept`, the recipient field `message.to` is defensively validated before being copied into a fixed 32-byte buffer: [1](#0-0) 

However, the `message.from` field — decoded from the same untrusted, attacker-influenced ABI payload (`Message::abi_decode(&body)`) — is used later, when optional calldata (`message.data`) is present and no signature was supplied, with no equivalent length check: [2](#0-1) 

Specifically:
- `H160::from_slice(&from_bytes[from_bytes.len() - 20..])` — if `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows the `usize` subtraction, producing either a panic (`attempt to subtract with overflow` in debug) or an out-of-range slice index panic (`range start index ... out of range for slice of length ...`) in release builds.
- `account.copy_from_slice(from_bytes)` — `copy_from_slice` panics unconditionally whenever the source slice length does not exactly equal the destination `[0u8; 32]` array's length (32).

This mirrors the CVE pattern: a copy/index operation sized by an attacker-controlled length field, missing the bounds check that its sibling routine (`to_bytes`) already has.

### Impact Explanation
A panic inside `on_accept` — which runs during ISMP message dispatch on the destination chain when delivering a cross-chain POST request — aborts the runtime execution for that request. Depending on how the runtime's `dispatch`/`execute` wraps module callbacks, an unhandled panic here can abort block execution or at minimum permanently and irrecoverably fail delivery of that specific commitment (since the request is marked as attempted/consumed by the router before or during `on_accept`), rendering the message stuck — a denial-of-service on a specific cross-chain transfer/route, consistent with the "route unable to deliver messages" acceptance criterion. This matches the CVSS 5.5 (`AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H`) profile of the source advisory: no confidentiality/integrity impact, but availability impact via crash/DoS.

### Likelihood Explanation
The `message.from` field is embedded in the ABI-encoded `body` of the incoming `PostRequest`. Only the *outer* ISMP request envelope's `from`/`source` pair (the dispatching contract address on the counterparty chain) is authenticated via `ContractToAsset::<T>::get(source, &from)`: [3](#0-2) 
The *inner* `message.from` bytes are whatever the counterparty-chain contract chose to ABI-encode into the request body — this repo cannot fully confirm from available context whether every EVM-side sender contract mapped into `ContractToAsset` rigidly always encodes exactly 20/32-byte `from` values, or whether some integration path allows a caller to influence this field directly (e.g. via a custom/older/third-party mapped sender contract, or a bug in an ancillary send path). Given the sibling `to_bytes` check exists precisely to guard against malformed lengths from the same untrusted body, the missing guard on `from_bytes` appears to be an oversight of the identical defensive pattern rather than an intentionally-trusted invariant.

### Recommendation
Add the same explicit length validation used for `to_bytes` before consuming `from_bytes`:
- For `source.is_evm()`: require `from_bytes.len() == 20` before calling `H160::from_slice`.
- For the non-EVM branch: require `from_bytes.len() == 32` before `copy_from_slice`.
Return `HftError::InvalidRecipientLength`-style errors (or a new `InvalidSenderLength` variant) instead of allowing `copy_from_slice`/slice-range panics to propagate.

### Proof of Concept
1. A contract mapped in `ContractToAsset` (or any path that lets an attacker control the ABI-encoded `Message.from` field of the request body, e.g. a permissively-designed integration contract) dispatches a POST request whose decoded `Message.from` is, say, 5 bytes, with non-empty `Message.data` and no `signature`.
2. On the destination Substrate chain, `pallet-ismp` delivers the request to `HyperFungibleToken::on_accept`.
3. Execution reaches the `else` branch at line 177; `from_bytes.len() - 20` underflows (source is EVM) or `account.copy_from_slice(from_bytes)` panics (source is not EVM), aborting message processing.

**Note on uncertainty:** I was unable to fully confirm, within the available codebase context, whether the canonical EVM-side `HyperFungibleToken.sol`/`WrappedHyperFungibleTokenUpgradeable.sol` `send()` implementations always constrain `message.from` to exactly 20/32 bytes for every contract address that can legitimately be registered in `ContractToAsset`, or whether some reachable integration path lets an unprivileged caller supply an arbitrary-length `from` value end-to-end. This affects the precise likelihood rating; the finding is reported based on the clear code-level asymmetry (validated `to_bytes` vs. unvalidated `from_bytes`) rather than a confirmed exploit trace through the EVM sender contract.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L54-56)
```rust
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
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
