Confirmed: `Message.from` in the pallet is declared as `bytes from;` — a variable-length ABI `bytes` field, not a fixed `address`/`bytes20`. That means its length is entirely attacker-controlled by whoever crafts the source-chain payload delivered through `on_accept`.

### Title
Unchecked `copy_from_slice` panic on attacker-controlled `Message.from` length in HFT on_accept - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`HyperFungibleToken::on_accept` decodes an ABI-encoded `Message` whose `from` field is an arbitrary-length `bytes` blob [1](#0-0) . When the calldata carries no signature and the request's `source` is not EVM, the code writes `from_bytes` directly into a fixed 32-byte stack buffer with no length check: [2](#0-1) .

### Finding Description
This is the same bug class as CVE-2024-31570 (unchecked variable-length attacker input copied into a fixed-size buffer): FreeImage's `PluginXPM.cpp` copied unbounded XPM color/pixel data into a fixed stack array; here, `account.copy_from_slice(from_bytes)` copies an unbounded ABI `bytes` value into a fixed `[u8; 32]` without first checking `from_bytes.len() == 32`. `Vec::copy_from_slice`/slice `copy_from_slice` panics if the source length differs from the destination length. The sibling code path a few lines below, `on_timeout`, explicitly handles this by branching on `len() == 32` / `len() == 20` and returning `HftError::InvalidSenderLength` otherwise [3](#0-2) , showing the maintainers were aware `from`/`to` lengths are untrusted — but the equivalent guard is missing in the `on_accept` non-EVM/no-signature branch.

Because `Message` is decoded straight from the cross-chain `PostRequest.body` via `Message::abi_decode(&body)` [4](#0-3) , an unprivileged relayer delivering any inbound token-transfer message from a registered source contract (`ContractToAsset` lookup only checks the source chain+contract pair, not the payload shape) can set `from` to any length other than 32 (e.g. 0, 1, 31, 33 bytes) while still supplying `to`/`amount` fields that pass validation, and by omitting `substrate_data.signature`, forcing execution into the vulnerable branch.

### Impact Explanation
`copy_from_slice` panicking inside pallet dispatch logic (`on_accept`, invoked from `pallet-ismp`'s message-handling extrinsic) turns into a runtime panic during block execution. In a Substrate/FRAME node this is typically caught at the transaction-execution boundary and converted into a dispatch error/module panic rather than corrupting memory (Rust's safety guarantees prevent a classic stack buffer overflow), but it can still deny relaying of that message and, depending on how the runtime handles panics-in-block-execution, risks aborting block production for that block, which is a route-unable-to-deliver-messages condition for the affected app/pallet — meeting the "route unable to deliver messages" impact bar for this scan even though it does not achieve memory corruption as in the original CVE.

### Likelihood Explanation
High: this requires only a single crafted cross-chain `PostRequest` from any account/contract already registered in `ContractToAsset` for a source chain — no privileged role, no governance action, and no special relayer trust is needed beyond normal message relaying, satisfying the "single relayed proof/dispatched request" reachability bar.

### Recommendation
Add the same explicit length check used in `on_timeout` to the `on_accept` non-EVM/no-signature branch before calling `copy_from_slice`, returning a `HftError::InvalidSenderLength`-style error for any length other than 32 (and optionally accept/left-pad 20-byte EVM addresses analogously to the EVM branch), rather than relying on the buffer sizes matching by convention.

### Proof of Concept
1. Register a source EVM contract for asset X via `ContractToAsset` as normal (governance/admin action independent of the attacker).
2. Craft `Message.abi_encode()` with `from = vec![]` (or any length != 32), a valid `to` (20 or 32 bytes), a valid `amount`, and `data = SubstrateCalldata { signature: None, runtime_call: <any valid encoded call> }.encode()`.
3. Relay this as the `body` of a `PostRequest` from a `source` state machine where `source.is_evm()` is `false` (e.g., a Substrate/parachain source, since `EvmToSubstrate::convert` path is only used when `source.is_evm()`).
4. `on_accept` reaches `account.copy_from_slice(from_bytes)` with `from_bytes.len() != 32`, panicking inside pallet execution [5](#0-4) .

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L59-59)
```rust
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
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
