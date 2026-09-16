### Title
Unbounded-depth SCALE decode of attacker-controlled cross-chain calldata in `pallet-hyper-fungible-token::on_accept` allows remote node crash via decode stack overflow - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token`'s `IsmpModule::on_accept` decodes a `RuntimeCall` directly from attacker-supplied bytes using the plain `Decode::decode` with no recursion-depth limit, unlike the sibling `call-decompressor` pallet in this same repo, which deliberately bounds `RuntimeCall` decoding with `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)` specifically because unbounded decode of a `RuntimeCall` is dangerous.

### Finding Description
`HyperFungibleToken.send()` on the EVM side accepts a fully user-controlled `data: bytes` field in `SendParams`/`Message`, documented as "optional calldata for CallDispatcher" [1](#0-0) . This `data` is ABI-encoded into the cross-chain `Message` body and dispatched as an ISMP POST request that any user can trigger by calling `send()` with `data` set to arbitrary bytes and no minimum-value/allowlisting on its contents.

On the Polkadot destination, `pallet_hyper_fungible_token`'s `on_accept` handler treats `message.data` as SCALE-encoded `SubstrateCalldata`, decodes it, and then decodes `substrate_data.runtime_call` (a raw `Vec<u8>` field) into the runtime's `RuntimeCall` type using the plain, unlimited `Decode::decode`: [2](#0-1) [3](#0-2) 

The `SubstrateCalldata.runtime_call` field is declared as an unbounded `Vec<u8>`: [4](#0-3) 

Because `RuntimeCall` in a Substrate runtime is a deeply-nested enum (it can recursively embed calls such as `Utility::batch(Vec<RuntimeCall>)`, `Proxy::proxy(RuntimeCall)`, etc.), naive `codec::Decode` recurses once per nested call with no bound on nesting depth. The project is aware of exactly this hazard: `pallet-call-decompressor`, which also decodes an attacker/relayer-supplied `RuntimeCall`, explicitly caps recursion via `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)` with `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT = 4` [5](#0-4) [6](#0-5) . `pallet-hyper-fungible-token`'s `on_accept` does not use this bounded decoder at all, and calls the unbounded `T::RuntimeCall::decode` on message-derived bytes that originate entirely from an untrusted, remote, unprivileged sender.

An attacker can craft a `data` payload whose SCALE encoding represents an extremely deeply nested `RuntimeCall` (e.g., thousands of nested `Utility::batch` / `Proxy::proxy` wrappers) small in byte size but large in decode-stack depth. Decoding such a structure on a machine with a fixed-size stack recursively calls into `Decode::decode` implementations for each nested variant, exhausting the stack and crashing the executing process (transaction-pool validation on `on_accept`/OnPost message execution during `pallet-ismp` message handling, i.e. `handle_unsigned` → module dispatch → `on_accept`).

### Impact Explanation
This message-handling path is reachable by any unprivileged actor that can call the EVM `HyperFungibleToken.send()`/`WrappedHyperFungibleToken.send()` function with a crafted `data` field, and is delivered onto the Polkadot side automatically once relayed and proven via `handle_unsigned`, which every node in the transaction pool must validate before inclusion [7](#0-6) . A crash during this validation path (during `validate_unsigned` execution, which calls `Self::execute(messages.clone())`) can be triggered on every full node/collator processing the unsigned extrinsic in the transaction pool, which is a remotely-triggerable denial-of-service against the parachain's block production/relaying — the route becomes unable to deliver ISMP messages once affected nodes repeatedly crash while re-processing the same or similarly crafted messages, which the "Validate" section explicitly recognizes as impact ("a route unable to deliver messages").

### Likelihood Explanation
High. The `data` field of `HyperFungibleToken`/`WrappedHyperFungibleToken.send()` is fully attacker-controlled with only ABI-encoding constraints, and the destination pallet decodes it into `RuntimeCall` with no depth or size bound, unlike the parallel `call-decompressor` pallet, which enforces exactly this bound. No signature, admin, or special privilege is required — only a normal `send()` call with a minimal token amount and the crafted `data` bytes, plus a relayer forwarding the proof (any unprivileged relayer suffices, since messages are unsigned/free to execute per `pallet-ismp`'s documented design) [8](#0-7) .

### Recommendation
Replace the unbounded `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` in `on_accept` (module.rs line 189) with a depth-limited decode, mirroring `pallet-call-decompressor`'s approach: use `codec::DecodeLimit::decode_all_with_depth_limit` (or equivalent) with a small, fixed recursion bound (e.g., the same `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT` constant), and reject the message (returning an error rather than panicking/crashing) if the bound is exceeded. Consider also bounding `SubstrateCalldata` and `runtime_call`'s byte length before decode to further reduce attack surface.

### Proof of Concept
1. Attacker calls `HyperFungibleToken.send()` (or `WrappedHyperFungibleToken.send()`) on a registered peer EVM chain with:
   - `to`: any valid recipient bytes
   - `amount`: minimal dust amount
   - `data`: ABI-encoding of `SubstrateCalldata { signature: None, runtime_call: <crafted deeply-nested SCALE bytes> }`, where `runtime_call` encodes something like `Utility::batch([Utility::batch([Utility::batch([... nested N times ...])])])` (or `Proxy::proxy(...)` chains) to a nesting depth large enough to exceed the default stack (a few thousand levels is typically sufficient, and each level costs only a few bytes of wire-encoding, so the whole payload remains small).
2. The message is relayed via ISMP; when the destination parachain node validates/executes the `handle_unsigned` extrinsic (or any relayer submits it and the module's `on_accept` runs), `SubstrateCalldata::decode` succeeds, and then `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` recurses once per nested level with no bound, exhausting the thread's stack and aborting the node process.
3. Confirming exact minimum nesting depth to trigger the crash and validating against the specific `RuntimeCall` type used in the target runtime would require running the actual runtime binary, which was not available in this indexed context — this should be verified in a local reproduction before filing as confirmed-exploitable, but the missing depth-limit guard (compared directly against the sibling `call-decompressor` pallet's mitigation for the identical class of bug) is confirmed in the source.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L80-93)
```text
    /**
     * @title Message
     * @notice The cross-chain message body for token transfers
     */
    struct Message {
        /// @notice The original sender on the source chain (used for timeout refunds)
        bytes from;
        /// @notice The recipient on the destination chain
        bytes to;
        /// @notice The amount of tokens being transferred
        uint256 amount;
        /// @notice Optional calldata to execute on the destination chain via CallDispatcher
        bytes data;
    }
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-122)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-196)
```rust
			let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
				.map_err(HftError::RuntimeCallDecodeError)?;
			// Apply the runtime's base call filter so that cross-chain calls cannot
			// reach dispatchables that the runtime has otherwise filtered out (e.g.
			// during a maintenance mode or a SafeMode period).
			if !<T as frame_system::Config>::BaseCallFilter::contains(&runtime_call) {
				Err(HftError::CallFiltered)?
			}
```

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L105-113)
```rust
/// SCALE-encoded calldata for executing a runtime call on the destination substrate chain
#[derive(Debug, Clone, Encode, Decode, scale_info::TypeInfo, PartialEq, Eq)]
pub struct SubstrateCalldata {
	/// Optional SCALE-encoded [MultiSignature](sp_runtime::MultiSignature) of the beneficiary's
	/// account nonce and the encoded runtime call
	pub signature: Option<Vec<u8>>,
	/// SCALE-encoded runtime call to execute
	pub runtime_call: Vec<u8>,
}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L46-51)
```rust
const ONE_MB: u32 = 1_000_000;
/// This is the maximum nesting level required to decode
/// the supported ismp messages and pallet_ismp_relayer calls
/// All suported call types require a recursion depth of 2 except calls containing Ismp Get requests
/// Ismp Get requests have a nested vector of keys requiring an extra recursion depth
const MAX_EXTRINSIC_DECODE_DEPTH_LIMIT: u32 = 4;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L149-153)
```rust
			let runtime_call = T::RuntimeCall::decode_all_with_depth_limit(
				MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
				&mut &decompressed[..],
			)
			.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;
```

**File:** modules/pallets/ismp/src/lib.rs (L614-626)
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

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```
