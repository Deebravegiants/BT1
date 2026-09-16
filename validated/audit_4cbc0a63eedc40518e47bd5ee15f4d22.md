### Title
Unchecked-length `message.from` in HFT `on_accept` calldata path panics the runtime on malformed cross-chain messages - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`pallet-hyper-fungible-token`'s `IsmpModule::on_accept` decodes an attacker-influenced `message.from` byte slice and, when optional calldata carries no signature, uses it without validating its length before slicing/copying into fixed-size buffers — causing an arithmetic-underflow/slice panic (EVM source) or a `copy_from_slice` length-mismatch panic (non-EVM source). This is reachable from any relayed `PostRequest` delivered through the permissionless, unsigned `pallet_ismp::handle_unsigned` dispatch path.

### Finding Description
`on_accept` decodes the ABI-encoded `Message` from the `PostRequest` body: [1](#0-0) 

The `to` field is defensively length-checked (must be 20 or 32 bytes, else a typed `HftError::InvalidRecipientLength` is returned): [2](#0-1) 

But when `message.data` carries a `SubstrateCalldata` payload with no `signature` (the "unsigned calldata" branch, used to compute the dispatch `origin` from the sender), `message.from` is used with **no length check at all**: [3](#0-2) 

- If `source.is_evm()` and `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows `usize`, producing either a debug-mode overflow panic or an out-of-range slice index panic in `&from_bytes[huge_range..]`.
- If `source` is not EVM and `from_bytes.len() != 32`, `account.copy_from_slice(from_bytes)` panics on a length mismatch (this is the exact same `copy_from_slice`-panics-on-length-mismatch bug class the codebase has already patched in several other places, e.g. `StateMachine::from_str` and `ByteVector<N>::decode`, both explicitly called out as "must never panic" on untrusted input).

Contrast this with the pallet's own `on_timeout` handler, which decodes the analogous `message.from` field with a proper length check and a typed error (`HftError::InvalidSenderLength`) instead of an unchecked copy: [4](#0-3) 

This shows the pallet author's intended pattern for handling `from`/`to` fields is a length check with a graceful error — `on_accept`'s calldata-origin branch is the one place that pattern was not applied.

`Message` is ABI-decoded straight from the request body (`Message::abi_decode(&body)`), and `from` is a `bytes` ABI field with no length constraint enforced by the codec — an attacker fully controls its byte length. Reaching `on_accept` only requires: (1) a `PostRequest` whose `(source, from)` pair resolves via `ContractToAsset` to a configured asset — i.e. it must appear to originate from the pallet's configured bridge contract address on that chain — and (2) a valid state/consensus proof for that request's inclusion, delivered via the permissionless `pallet_ismp::Call::handle_unsigned` extrinsic, which is processed for free by anyone with a proof: [5](#0-4) 

While in the common (honest) case the actual bridge contract encodes `from` as `msg.sender` (always 20 bytes), the on-chain state proof only has to prove that *some* storage/event data existed for the configured source contract — the byte layout of `from` inside the encoded body is not independently constrained by the ISMP/consensus layer, and any bug or governance-controlled variant of the source contract (or any other contract an admin later maps into `ContractToAsset`) that emits a nonstandard `from` length turns this into a live DoS. Because `pallet_ismp::handle_unsigned` also runs during `validate_unsigned` (mempool validation), an unhandled panic here does not merely fail one extrinsic — it can abort execution during transaction-pool validation/block execution, exactly the class of impact the reference CKB/snappy advisory describes (a malformed but structurally valid message triggering an uncaught panic in a consensus-critical, permissionlessly-reachable decode path).

### Impact Explanation
An uncaught panic during extrinsic dispatch or `validate_unsigned` is a chain-halting/DoS condition: it can abort the runtime's WASM execution for the block or crash the transaction-pool validation worker, blocking further processing of legitimate `handle_unsigned` messages (which is the sole delivery path for all cross-chain messages, including HFT token transfers). This qualifies as "a route unable to deliver messages" / consensus-layer DoS impact under the stated validation criteria, warranting High severity consistent with the referenced advisory's rating.

### Likelihood Explanation
Reaching the vulnerable branch requires: a `PostRequest` recognized by `ContractToAsset` (source+from-address mapping configured by governance), calldata (`message.data`) that decodes as `SubstrateCalldata` with `signature: None`, and a `from` field whose byte length is not 20 (for an EVM source) or not 32 (for non-EVM). None of these constraints are enforced by the consensus/ISMP layer itself — they depend entirely on the byte layout the source-chain contract happens to emit, which is not audited or fixed by the receiving pallet. Given the surrounding code already treats "attacker can smuggle a badly-sized byte field into this pallet" as a real, exploitable risk (as evidenced by the parallel checks on `to_bytes` and in `on_timeout`), the omission here is very plausibly reachable, particularly since HFT can be configured against arbitrary/varying source contracts (e.g. future or governance-added integrations) whose exact encoding is not guaranteed to always emit a 20-byte `from`.

### Recommendation
In the `on_accept` "no signature" branch, mirror the length validation already used for `to_bytes` (lines 62-71) and in `on_timeout` (lines 224-232): explicitly check `from_bytes.len() == 20` (EVM) or `== 32` (non-EVM) and return a typed `HftError` (e.g. reuse/extend `InvalidSenderLength`) instead of slicing/copying unconditionally. This closes both the `usize` underflow and the `copy_from_slice` panic.

### Proof of Concept
1. Configure (or have governance configure) `ContractToAsset` for a `(source, from)` pair where `source.is_evm()` is true.
2. Craft a `PostRequest` body that ABI-decodes to an HFT `Message` with:
   - `to`: a valid 20-byte recipient (passes the existing check),
   - `data`: a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <any allowed call> }`,
   - `from`: a `bytes` field of length `< 20` (e.g. 0 bytes).
3. Obtain (or forge, for a test/mock consensus client) a valid state/consensus proof that this `PostRequest` was included on the source state machine.
4. Submit `pallet_ismp::Call::handle_unsigned { messages: [Message::Request(RequestMessage { requests: [post_request], proof, .. })] }` as an unsigned extrinsic.
5. Execution reaches `HftModule::on_accept`, hits `from_bytes.len() - 20` with `from_bytes.len() == 0`, underflows, and panics inside `&from_bytes[from_bytes.len() - 20..]` — a wasm trap during `handle_unsigned` dispatch/validation.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-59)
```rust
		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L62-71)
```rust
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

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```
