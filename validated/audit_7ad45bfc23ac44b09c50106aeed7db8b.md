Based on my investigation, I found a concrete analog: unsanitized attacker-controlled data extracted from an authenticated cross-chain message is used unchecked in a data operation, where the only "guard" is a check on a different field — mirroring the Emlog pattern where an unfiltered field survives an unrelated authentication check.

### Title
Unvalidated `message.from` length causes panic/DoS on incoming HFT transfers with calldata - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`HyperFungibleToken::on_accept` authenticates the ISMP `PostRequest.from` (the source contract address) against `ContractToAsset`, but the `message.from` field *inside* the ABI-decoded message body is fully attacker-controlled, arbitrary-length bytes. When the message carries calldata (`message.data` non-empty) with no `substrate_data.signature`, this raw `message.from` is used directly for account derivation without a length check, unlike the sibling `to`/`from` conversions elsewhere in the same file that explicitly validate length and return `InvalidRecipientLength`/`InvalidSenderLength`.

### Finding Description
In `on_accept`, the `ContractToAsset::<T>::get(source, &from)` check only authenticates the *ISMP request's* `from` field (the registered peer contract) [1](#0-0) . It does not constrain `message.from`, which is decoded from the attacker-influenced ABI body via `Message::abi_decode(&body)` [2](#0-1) .

When `message.data` is non-empty and no signature is supplied, the code computes the dispatch origin from `message.from` with no length validation:

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
``` [3](#0-2) 

This is the exact same field (`message.from`) that, in the timeout handler `on_timeout`, is explicitly length-checked and rejected with `HftError::InvalidSenderLength` if not exactly 20 or 32 bytes [4](#0-3) . The same defensive pattern exists for `message.to` in `on_accept` itself [5](#0-4) , proving the length check is the intended guard that was omitted in this one branch.

Two concrete failure modes:
1. **EVM source, `from_bytes.len() < 20`**: `from_bytes.len() - 20` underflows a `usize`. In debug/checked builds this panics; in release (wrapping) builds it produces a huge index into `&from_bytes[...]`, which then panics on out-of-bounds slicing.
2. **Non-EVM source, `from_bytes.len() != 32`**: `copy_from_slice` panics directly on a length mismatch.

Both panics occur inside pallet dispatch (`on_accept`), which is executed by the ISMP router while processing a relayed message — a panic here aborts block execution for that transaction (and, depending on runtime panic handling, can affect the whole block), a resource/liveness impact on message delivery.

### Impact Explanation
This is reachable by any user of the source-chain `HyperFungibleToken` contract who can set an arbitrary `message.from` and non-empty `message.data` with no signature, then have a relayer deliver it (relayers are permissionless dispatchers of already-committed messages). It does not require a malicious relayer, admin, or governance action — only a single crafted cross-chain token transfer. The result is a route that becomes unable to deliver messages (a panicking dispatchable poisons that specific message/transaction execution, and depending on Substrate transaction/panic-handling configuration can disrupt normal `on_accept` processing for the pallet), satisfying the "route unable to deliver messages" impact bucket.

### Likelihood Explanation
Likelihood is high for any deployment of `hyper-fungible-token` pallet paired with calldata-carrying transfers: it requires no privileged capability, no bypassing of the ISMP consensus/membership proof (the request is legitimately delivered), and no additional signature (the vulnerable branch is precisely the `substrate_data.signature.is_none()` path). The attacker only needs to control the ABI-encoded `Message.from`/`Message.data` fields when calling `send()` on the source-chain contract (or crafting an equivalent cross-chain POST body), which is standard user-level access.

### Recommendation
Add the same length validation used elsewhere in this file (and in `on_timeout`) before deriving the dispatch origin from `message.from` in the unsigned branch: require `from_bytes.len() == 20` for EVM sources (reject otherwise via a new `HftError::InvalidSenderLength`/similar) and `from_bytes.len() == 32` for non-EVM sources before `copy_from_slice`, mirroring the existing `to`/`on_timeout` checks instead of assuming trusted length.

### Proof of Concept
1. On an EVM source chain, call `HyperFungibleToken.send(...)` (or construct an equivalent cross-chain POST body) with `Message.from` set to fewer than 20 bytes (e.g., 5 bytes) and `Message.data` set to a non-empty ABI-encoded `SubstrateCalldata` with `signature = None`.
2. Have any relayer deliver the resulting `PostRequest` to the destination hyperbridge parachain running `hyper-fungible-token`.
3. `on_accept` passes the `ContractToAsset` source-contract check (since that only validates the ISMP `from`, not `message.from`), decodes the message, mints/transfers as normal, then reaches the unsigned-origin branch and executes `from_bytes.len() - 20`, underflowing/panicking or slicing out of bounds — aborting execution of that message instead of returning a typed error, unlike the analogous `on_timeout` path which correctly rejects malformed lengths. [3](#0-2)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L54-56)
```rust
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-59)
```rust
		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L61-71)
```rust
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
