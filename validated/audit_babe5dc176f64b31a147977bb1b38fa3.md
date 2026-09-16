### Title
Out-of-bounds slice indexing on attacker-controlled `Message.from` in HFT calldata dispatch panics the runtime - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallets/hyper-fungible-token`'s `on_accept` handler derives the calldata-dispatch origin from the ABI-decoded `Message.from` field without validating its length, then slices/copies it into fixed-size buffers. A relayed `PostRequest` whose body encodes a `from` field shorter than 20 (EVM) or not exactly 32 (Substrate) bytes causes an unchecked subtraction/slice-length panic, mirroring the "crafted input drives an out-of-bounds memory access" bug class of CVE-2026-0899, but here reachable by any account dispatching a cross-chain token message.

### Finding Description
`on_accept` in [1](#0-0)  ABI-decodes the message body directly from the incoming `PostRequest`. Unlike the `to` field, which is explicitly length-checked (`InvalidRecipientLength`) at [2](#0-1) , the `from` field carries no such check when calldata is present: [3](#0-2) 

When `message.data` is non-empty and `substrate_data.signature` is `None`, the code executes:
```rust
let from_bytes = message.from.as_ref();
if source.is_evm() {
    T::EvmToSubstrate::convert(H160::from_slice(&from_bytes[from_bytes.len() - 20..]))
} else {
    let mut account = [0u8; 32];
    account.copy_from_slice(from_bytes);
    account.into()
}
```
- If `source.is_evm()` and `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows a `usize`. Whether this traps immediately (overflow checks) or wraps to a huge start index, the subsequent slice indexing panics with an out-of-bounds range error.
- On the non-EVM branch, `copy_from_slice` panics whenever `from_bytes.len() != 32`.

`message.from` is an arbitrary-length `bytes` field fully controlled by whoever calls the source-chain HFT contract (e.g. `HyperFungibleToken.sol`) that constructs and dispatches the ISMP `PostRequest` body — it is not the authenticated ISMP `PostRequest.from` sender, and no other code path bounds its length before this point.

### Impact Explanation
This is reachable from a single relayed message through the standard dispatch/delivery path (`pallet_ismp::handle_unsigned` → module routing → `HyperFungibleToken::on_accept`), i.e. exactly the "unprivileged relayed request" surface called out in scope. A panic raised inside on-chain message execution is a Denial of Service on message delivery for that request: any retry of the same malformed message reproduces the panic deterministically, permanently preventing that message (and, depending on how the runtime panic propagates through `#[frame_support::transactional]`/block execution, potentially other messages in the same batch) from being delivered — matching the "route unable to deliver messages" acceptance criterion. Because the same code path also silently uses unauthenticated `from` bytes as a dispatch origin when no signature is supplied, this is an internal correctness bug on the token-bridge's most privileged code path (arbitrary runtime-call dispatch), raising the severity above a simple panic.

### Likelihood Explanation
High. Constructing a `Message` with a `from` field of length ≠ 20 (EVM source) or ≠ 32 (non-EVM source) while still supplying non-empty `data` requires no special privilege — it is just a crafted ABI-encoded payload from the source-chain contract, analogous to the "crafted HTML page" trigger in the referenced CVE. No signature, consensus-proof forgery, or governance access is needed; only a normal PostRequest with a valid (but adversarially shaped) body needs to be relayed and proven, which any relayer can do.

### Recommendation
Validate `message.from.len()` before use, exactly as is already done for `message.to` (returning `HftError::InvalidSenderLength` for both branches), and reject calldata execution whose "no signature" path uses `from` as an origin — either require a verified signature to authorize `runtime_call` dispatch, or otherwise ensure the derived origin cannot be spoofed by attacker-supplied bytes.

### Proof of Concept
1. On the EVM source chain, dispatch an HFT message whose ABI-encoded body has: `to` = valid 20/32-byte recipient, `amount` = anything, `data` = non-empty calldata blob whose decoded `SubstrateCalldata.signature` is `None`, and `from` = e.g. a 1-byte value (`0x00`).
2. Relay the resulting `PostRequest` with a valid consensus/state proof through `pallet_ismp::handle_unsigned`.
3. Execution reaches [4](#0-3) , where `from_bytes.len() - 20` underflows / the following slice indexing panics, aborting message execution for that request.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-59)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

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
