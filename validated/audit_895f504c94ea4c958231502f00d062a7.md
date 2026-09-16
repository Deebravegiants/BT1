### Title
Missing length validation on attacker-controlled `message.from` causes a panic (trap) in `HyperFungibleToken` calldata dispatch - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`IsmpModule::on_accept` for the `hyper-fungible-token` pallet decodes an ABI-encoded cross-chain transfer `Message` from an untrusted `PostRequest.body` and, when the message carries unsigned calldata, derives the dispatch `origin` directly from `message.from` without validating its length — unlike the sibling path in `on_timeout`, which explicitly checks the length and returns a typed error.

### Finding Description
In `modules/pallets/hyper-fungible-token/src/module.rs`, `on_accept` decodes the incoming message with `Message::abi_decode(&body)` at line 59. `message.from` is an ABI `bytes` field controlled by whatever contract calls the source-chain `HyperFungibleToken` (any unprivileged sender who can trigger a cross-chain transfer), so its length is attacker-chosen, not fixed at 20 or 32 bytes.

When `message.data` is non-empty and `substrate_data.signature` is `None` (unsigned calldata path), the code does: [1](#0-0) 
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
- If `source.is_evm()` and `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows/produces an out-of-range index, and the subsequent slice indexing panics (trap) rather than returning a controlled error.
- If `source` is not EVM and `from_bytes.len() != 32`, `copy_from_slice` panics on a length mismatch.

This is the exact bug class cited in CVE-2024-32617: an unchecked length assumption on attacker-influenced data feeding a raw memory operation (`strdup`/`copy_from_slice`/slice indexing) without a prior bounds check — the same pattern the codebase explicitly documents and fixes elsewhere, e.g. `StateMachine::from_str`'s regression test noting "the id is copied into a `[u8; 4]`, and `copy_from_slice` traps on a length mismatch... reachable from untrusted input", and the `as_utf8_string` deserializer that used to crash the RPC worker the same way: [2](#0-1) [3](#0-2) 

Notably, the pallet's own `on_timeout` handler for the *same* `message.from` field explicitly guards against exactly this: [4](#0-3) 
```
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
The `on_accept` unsigned-calldata path lacks this equivalent check, which is the root cause.

### Impact Explanation
Minting/transfer to the beneficiary happens earlier in `on_accept` (lines 94–117) before the vulnerable calldata block executes: [5](#0-4) 
A crafted `message.from` of length other than 20/32, combined with non-empty `message.data` and no signature, causes the runtime to panic mid-dispatch. Whether this reverts the already-applied mint/transfer depends on FRAME's transactional storage semantics around `on_accept`'s invocation from `pallet-ismp`'s message handler, which I was not able to fully trace in the available index (this pallet-ismp dispatch wrapper wasn't retrieved). At minimum this is a reliable, attacker-triggerable panic reachable from a single cross-chain POST message body crafted by any unprivileged sender on the source chain, directly matching the "route unable to deliver messages" acceptance criterion — the affected request becomes unprocessable/stuck. If the transactional boundary does not roll back the preceding mint, this becomes an unbacked-mint/fund-freezing bug instead, which I could not confirm from the indexed code.

### Likelihood Explanation
High: any account able to call `HyperFungibleToken.send` (or equivalent) on a supported source chain and later attach non-empty, unsigned calldata with an `on_accept` message whose `from` field is not exactly 20 or 32 bytes can trigger this deterministically. No special privileges, timing, or race conditions are required — a single relayed message suffices.

### Recommendation
Add the same explicit length check used in `on_timeout` to the `on_accept` unsigned-calldata branch before indexing/copying `from_bytes`, returning a typed `HftError` (e.g. `InvalidSenderLength`) instead of allowing the slice/copy to panic.

### Proof of Concept
1. On the source EVM chain, call the `HyperFungibleToken` send function such that the resulting ABI-encoded `Message.from` field is populated with a byte string of length other than 20 or 32 (e.g., 19 bytes), and set `Message.data` to non-empty unsigned calldata (`SubstrateCalldata` with `signature: None`).
2. Relay the resulting `PostRequest` to the destination Substrate chain running the `hyper-fungible-token` pallet.
3. `on_accept` decodes the message, mints/transfers per lines 93–117, then reaches the unsigned-calldata branch at lines 176–186, where `from_bytes.len() - 20` underflows (EVM source) or `copy_from_slice` panics (non-EVM source), aborting the extrinsic.
4. Repeat for any relayed message meeting these conditions to reliably block message processing for that request/route.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L93-117)
```rust
		// Mint or transfer to beneficiary
		if local_asset_id == T::NativeAssetId::get() {
			<T as Config>::NativeCurrency::transfer(
				&Pallet::<T>::pallet_account(),
				&beneficiary,
				amount,
				ExistenceRequirement::AllowDeath,
			)
			.map_err(|e| HftError::TransferFailed(e.into()))?;
		} else {
			let is_native = NativeAssets::<T>::get(local_asset_id.clone());
			if is_native {
				<T as Config>::Assets::transfer(
					local_asset_id,
					&Pallet::<T>::pallet_account(),
					&beneficiary,
					amount.into(),
					Preservation::Expendable,
				)
				.map_err(|e| HftError::TransferFailed(e.into()))?;
			} else {
				<T as Config>::Assets::mint_into(local_asset_id, &beneficiary, amount.into())
					.map_err(|e| HftError::MintFailed(e.into()))?;
			}
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

**File:** modules/ismp/core/src/host.rs (L470-474)
```rust
	// A malformed `SUBSTRATE-`/`TNDRMINT-` id whose byte length is not exactly 4
	// must return an error rather than panic. The id is copied into a `[u8; 4]`,
	// and `copy_from_slice` traps on a length mismatch — in the runtime this is a
	// wasm trap reachable from untrusted input (e.g. `BandwidthManager.purchase`),
	// so the length is now checked up-front (matching the `RELAY-` arm).
```

**File:** modules/utils/serde/src/lib.rs (L529-532)
```rust
	// `as_utf8_string` deserializes into a fixed `[u8; 4]`. It used to `copy_from_slice`
	// straight from the input, which panics on any length mismatch — and it runs on
	// untrusted RPC input (`consensus_state_id`), so the panic aborted the node's `rpc`
	// worker thread and took the process down. Wrong lengths must be serde errors.
```
