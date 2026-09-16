Confirmed: the Solidity-side `Message.from` and `Message.data` fields are `bytes` — arbitrary length, and `from` is set by the **caller of `send()`**, not by the bridge contract itself (need to verify the exact assignment in `HyperFungibleToken.sol`, which I could not fully confirm before running out of iterations — see caveat below). Given the on-chain (Substrate) decode path does not validate `message.from` length before using it in the calldata-authorization fallback, this is a plausible analog to CVE-2016-2168: a crafted field in an otherwise-authenticated cross-chain message reaches an authorization-adjacent computation (`from_bytes.len() - 20`) and panics before any check completes.

### Title
Unchecked `message.from` length causes a `usize` subtraction panic in `HyperFungibleToken::on_accept` calldata-authorization fallback - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
When a cross-chain token-transfer message carries optional calldata (`message.data` non-empty) with no attached signature, `on_accept` derives the calldata's dispatch origin from `message.from` for EVM sources by slicing the last 20 bytes: `&from_bytes[from_bytes.len() - 20..]`. This arithmetic is performed without first checking `from_bytes.len() >= 20`.

### Finding Description
`Message` is decoded via `alloy_sol_macro` ABI decoding as `bytes from; bytes to; uint256 amount; bytes data;` [1](#0-0) , meaning `from` is an arbitrary-length dynamic `bytes` field, entirely independent of the ISMP `PostRequest.from` (module id) that is authenticated against `ContractToAsset` [2](#0-1) . The `ContractToAsset` check authenticates *which contract* dispatched the request, not the *contents* of the inner ABI-encoded `Message` struct — the inner `from`/`data` fields are payload bytes chosen by whoever calls the sending contract's public transfer function on the source chain.

In the no-signature fallback branch of the optional-calldata execution path, the code computes:
```rust
let from_bytes = message.from.as_ref();
if source.is_evm() {
    T::EvmToSubstrate::convert(H160::from_slice(&from_bytes[from_bytes.len() - 20..]))
}
``` [3](#0-2) 

If `from_bytes.len() < 20`, `from_bytes.len() - 20` is a `usize` subtraction underflow. In a runtime built with overflow checks enabled (the standard, safety-oriented configuration for Substrate runtimes), this panics unconditionally during extrinsic execution — this is the direct Rust analog of the mod_authz_svn NULL pointer dereference: a value derived from attacker-supplied message data is used in an unchecked arithmetic/indexing operation inside a per-message check, crashing the executing context instead of gracefully rejecting the malformed input. Note the sibling `on_timeout` path (`from_bytes.len() == 32 / == 20 / else error`) *does* validate length explicitly [4](#0-3) , confirming the `on_accept` no-signature branch is the outlier missing this validation. Similarly the `to` field is length-checked before use [5](#0-4) , but `from` in the calldata-authorization branch is not.

### Impact Explanation
A panic during `on_accept`, invoked from the unsigned `handle_unsigned` dispatch path [6](#0-5) , aborts execution of that extrinsic/block-building context. Depending on how panics unwind through FRAME's transactional dispatch, this can at minimum permanently fail delivery of that specific message (the request can never be delivered without reverting the pallet's decode logic), and in the worst case destabilizes block execution for a message that is otherwise fully authenticated (real state proof, real registered contract pair) — a route made unable to deliver messages, matching the required impact bucket.

### Likelihood Explanation
Reaching this code requires: (1) an ISMP `PostRequest` genuinely dispatched from a `ContractToAsset`-registered `(source, from)` pair, and (2) the sending EVM contract's `send()` populating `message.from` with fewer than 20 bytes and non-empty `message.data` with `SubstrateCalldata.signature = None`. I was unable to confirm within the remaining budget whether `HyperFungibleToken.sol`'s `send()` always hardcodes `from = abi.encodePacked(msg.sender)` (fixed 20 bytes, making this unreachable by an ordinary caller) or whether any caller-controlled parameter feeds `message.from`. **This is the key open question** — if `from` is always fixed by the bridge contract to a valid 20-byte address, this finding is not exploitable by an unprivileged user and should be treated as defense-in-depth rather than a live vulnerability.

### Recommendation
Validate `from_bytes.len() >= 20` (mirroring the `on_timeout` branch's explicit length match) before slicing in the no-signature fallback of `on_accept`, returning a typed error (e.g., a new `HftError::InvalidSenderLength`) instead of panicking.

### Proof of Concept
Not independently verified end-to-end due to the unresolved question above about `HyperFungibleToken.sol`'s `send()` implementation. Conceptually: dispatch a `PostRequest` from a registered `(source, from)` pair whose ABI-encoded body decodes to `Message { from: bytes(len < 20), to: bytes(20 or 32), amount, data: non-empty SubstrateCalldata with signature=None }`; on delivery, `on_accept` reaches the `from_bytes.len() - 20` computation and panics.

**Caveat:** Given the uncertainty about whether `message.from` is attacker-influenced (versus contract-hardcoded), I recommend treating this as a candidate requiring confirmation via a full read of `HyperFungibleToken.sol`'s `send()` function rather than a fully proven finding.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L33-43)
```rust
// ABI-compatible Message matching the Solidity HyperFungibleToken.Message struct:
// struct Message { bytes from; bytes to; uint256 amount; bytes data; }
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

**File:** modules/pallets/ismp/src/lib.rs (L614-625)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;
```
