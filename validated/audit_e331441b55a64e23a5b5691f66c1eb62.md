### Title
Panic via unvalidated attacker-controlled slice length in `on_accept` beneficiary/origin derivation - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
CVE-2018-17101 is a class of bug where fixed-size buffer writes are performed using a length taken from untrusted input without validating that the input matches the expected size, causing an out-of-bounds write/crash. The `HyperFungibleToken` pallet's `on_accept` handler contains an analogous pattern: it copies an attacker-controlled, variable-length `bytes` field directly into a fixed-size `[u8; 32]` buffer (or slices it with an unchecked length-based offset) without validating the length beforehand, which panics the runtime on malformed input.

### Finding Description
In `on_accept`, when the ABI-decoded `Message.data` carries `SubstrateCalldata` with `signature: None`, the code derives the transaction `origin` directly from the message's `from` field: [1](#0-0) 

```
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

`message.from` is a `bytes` field of the ABI struct `Message` decoded at line 59 (`Message::abi_decode(&body)`), and is entirely attacker-controlled — it is not validated for length anywhere before this point, unlike the sibling `to_bytes`/`beneficiary_bytes` handling a few lines above, which explicitly checks `to_bytes.len() == 32` or `== 20` and returns `HftError::InvalidRecipientLength` otherwise: [2](#0-1) 

No equivalent length check exists for `from_bytes`:
- If `source.is_evm()` is true and `from_bytes.len() < 20`, the subtraction `from_bytes.len() - 20` underflows (usize), producing either a debug-mode overflow panic or, in release mode, an out-of-range slice index that panics on bounds-check.
- If `source.is_evm()` is false and `from_bytes.len() != 32`, `account.copy_from_slice(from_bytes)` panics immediately because Rust enforces equal-length slices for `copy_from_slice`.

Both are directly reachable from a fully attacker-controlled cross-chain message body — the only prior authentication is `ContractToAsset::<T>::get(source, &from)` at line 55, which authenticates the **outer** ISMP `PostRequest.from` (the sending contract), not the **inner** ABI-decoded `message.from` field that is later misused as the account-derivation input.

### Impact Explanation
A single malicious/crafted cross-chain `PostRequest` delivered by any unprivileged relayer to the `HyperFungibleToken` module (as long as the sending contract is a registered/whitelisted bridge contract for some asset, which is the normal operating condition for this pallet) can trigger a runtime panic inside `on_accept`. Since `on_accept` executes as part of ISMP request dispatch within block/extrinsic execution, a panic here aborts execution non-gracefully instead of returning a routed `Result::Err`, which is a denial-of-service on the pallet's message-delivery pipeline — directly matching the CVE's "denial of service (application crash)" impact class, translated to "a route unable to deliver messages" in the target impact set.

### Likelihood Explanation
High. The vulnerable code path requires only:
1. An attacker (or malicious contract on an already-registered source chain) constructing a `Message.data` payload where `SubstrateCalldata.signature = None`.
2. Setting `Message.from` to a byte string whose length is not 20 (when `source.is_evm()`) or not 32 (when not EVM).

No cryptographic proof, governance action, or privileged role is required beyond the ability to send a message through an already-authorized bridge contract — which any user of the bridge is expected to be able to trigger via the normal token-transfer flow, since `from` is attacker-supplied application data, not protocol-enforced.

### Recommendation
Add explicit length validation for `from_bytes` mirroring the existing `to_bytes` check, returning a typed error (e.g., `HftError::InvalidSenderLength`) instead of allowing the runtime to panic:
```rust
let from_bytes = message.from.as_ref();
let origin = if source.is_evm() {
    if from_bytes.len() < 20 {
        Err(HftError::InvalidSenderLength(from_bytes.len()))?;
    }
    T::EvmToSubstrate::convert(H160::from_slice(&from_bytes[from_bytes.len() - 20..]))
} else {
    if from_bytes.len() != 32 {
        Err(HftError::InvalidSenderLength(from_bytes.len()))?;
    }
    let mut account = [0u8; 32];
    account.copy_from_slice(from_bytes);
    account.into()
};
```

### Proof of Concept
1. Craft an EVM `HyperFungibleToken.Message` with `to` = valid 32/20-byte recipient, `amount` valid, and `data` set to an ABI-encoded `SubstrateCalldata { signature: None, runtime_call: <any> }`.
2. Set `Message.from` to a byte string of length 0 (or any length other than 20/32), e.g. empty bytes.
3. Dispatch this as the body of an ISMP `PostRequest` from a contract address already registered in `ContractToAsset` for the target asset/source chain (the normal HFT bridging path).
4. On delivery, `on_accept` reaches `from_bytes.len() - 20` (if `source.is_evm()`) or `account.copy_from_slice(from_bytes)` (otherwise), both of which panic given the crafted length, aborting execution of the request-handling code path.

### Citations

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
