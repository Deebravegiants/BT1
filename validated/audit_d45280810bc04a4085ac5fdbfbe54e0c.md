## Analysis

I found a valid analog. The pattern in the CVE (empty/short attacker-controlled input driving an unchecked read past bounds) reappears in `pallet-hyper-fungible-token`'s calldata-signature path, in contrast to the same pallet's `to`-field handling just a few lines above it, which is correctly length-checked. [1](#0-0) 

### Title
Unchecked-length slice on attacker-controlled `message.from` causes a runtime panic (DoS) in `pallet-hyper-fungible-token::on_accept` - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` (the `IsmpModule` handler invoked for every incoming HFT/WrappedHFT ISMP `PostRequest`) computes the calldata-signing origin as `from_bytes[from_bytes.len() - 20..]` without first checking `from_bytes.len() >= 20`. `from_bytes` is `message.from`, an attacker-supplied ABI field of the cross-chain `Message` struct decoded straight from the untrusted request body. [2](#0-1) 

### Finding Description
`on_accept` is reached whenever an EVM-side `HyperFungibleToken`/`WrappedHyperFungibleToken` contract dispatches a POST request that lands on a Substrate chain running `pallet-hyper-fungible-token`. The message body is ABI-decoded with no restriction on `from`'s length: [3](#0-2)  and on the EVM sender side `from` is normally `abi.encodePacked(msg.sender)` (20 bytes), [4](#0-3)  — but nothing on the receiving Substrate side enforces that length, and the `body` is fully attacker-controlled since it is only authenticated by the *source contract address*, not the message payload contents (`ContractToAsset::get(source, &from)` and later `Message::abi_decode(&body)`; the ABI decoder places no length floor on the dynamic `bytes from` field, so a caller of the peer contract's cross-chain send function can freely choose an empty/short `from`).

When `message.data` is non-empty and the embedded `SubstrateCalldata` carries no signature, the pallet falls into the `else` branch and does `&from_bytes[from_bytes.len() - 20..]`. If `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows the `usize` subtraction. Under a `overflow-checks = true`/debug-style build this panics with an arithmetic-overflow trap; under a release build (`overflow-checks = false`, the Substrate default for runtime wasm) it wraps to a huge index, and the subsequent slice indexing panics with an out-of-bounds error. Either way the effect is a wasm trap — this is precisely the same bug class as `ALPINE-CVE-2016-10197` (`search_make_new` in libevent indexing into an attacker-supplied empty string without a length check, causing an out-of-bounds read).

This directly contrasts with the pallet's own handling of the sibling field just above it, `message.to`, which explicitly validates length before use: [5](#0-4) . No equivalent guard exists for `message.from` in the calldata-execution branch.

The very similar `else` branch for the 32-byte substrate case is also unguarded: `account.copy_from_slice(from_bytes)` panics if `from_bytes.len() != 32`. [6](#0-5) 

### Impact Explanation
`handle_unsigned` (pallet-ismp's unsigned extrinsic that any unprivileged relayer can submit with a valid membership proof) dispatches incoming ISMP messages, which in turn calls `IsmpRouter` to route to `pallet-hyper-fungible-token::on_accept`. [7](#0-6)  A panic inside `on_accept`, reached from a `#[frame_support::transactional]` unsigned call executed during block authoring/validation, traps the wasm runtime. Because ISMP's `Execute`/`validate_unsigned` path re-runs `Self::execute(...)` during transaction pool validation and again on-chain, a reachable panic here is a denial-of-service vector against block production/import for any chain running this pallet with the calldata-dispatch feature enabled — a message deliverer (anyone relaying a legitimate cross-chain send with an attacker-crafted `data`/`from` combination) can halt processing of `handle_unsigned` batches containing the malicious message.

### Likelihood Explanation
Reaching this code requires only that: (1) the source contract is a legitimate registered peer under `ContractToAsset`, and (2) the message includes non-empty `data` with `SubstrateCalldata.signature == None`, and a `from` field shorter than 20 bytes (for the EVM-source branch) or not exactly 32 bytes (for the non-EVM branch). Since `from` is attacker-controlled ABI bytes chosen at dispatch time on the sending EVM/Substrate side — not derived on-chain from `msg.sender` by the receiving pallet — any user able to call the sending app's `send`-equivalent function (or, more directly, anyone constructing the ISMP message/proof pair delivered via `handle_unsigned`) can set an arbitrarily short `from`. This makes the trigger straightforward and reachable from a single relayed message; likelihood is high.

### Recommendation
Before slicing, validate `from_bytes.len()` exactly as `to_bytes` is validated a few lines earlier: return `HftError::InvalidRecipientLength(from_bytes.len())` (or an analogous new error) when `from_bytes.len() != 20` in the EVM branch and `!= 32` in the substrate branch, instead of performing unchecked arithmetic/slicing. Add regression tests mirroring the `empty_hp_prefix_returns_error_not_panic` / `from_str_rejects_non_four_byte_consensus_ids` pattern already used elsewhere in this codebase for this exact bug class.

### Proof of Concept
1. Register a peer contract for chain `source` via `ContractToAsset` (normal chain setup).
2. From the EVM side (or by directly crafting the ISMP `PostRequest`), send a POST request whose ABI-encoded body is `Message { from: b"" /* 0 bytes */, to: <valid 20 or 32 bytes>, amount: X, data: <non-empty SubstrateCalldata with signature = None> }`.
3. Relay this request to the Substrate chain via `pallet_ismp::Call::handle_unsigned` with a valid membership proof.
4. During `Pallet::<T>::execute`, `on_accept` reaches `let from_bytes = message.from.as_ref();` with `from_bytes.len() == 0`, computes `0usize - 20`, and the resulting slice index panics/traps, aborting extrinsic execution (and, depending on build/overflow-checks configuration, halting block processing of the containing block).

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L177-187)
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
			};
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L241-246)
```text
        bytes memory body = abi.encode(Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));
```

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
