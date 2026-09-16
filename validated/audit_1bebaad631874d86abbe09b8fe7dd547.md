## Analog Found: Unbounded, Fee-less Cryptographic Verification in `validate_unsigned` — Uncontrolled Resource Consumption

### Title
Unsigned ISMP message batches force full cryptographic/proof verification during transaction-pool validation with no batch-size or cost bound, enabling free CPU exhaustion of every relaying node — (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic is deliberately free and unauthenticated (`ensure_none` origin), and its `ValidateUnsigned::validate_unsigned` hook runs the *entire* message-execution path — `Self::execute(messages.clone())`, which performs full consensus/state proof verification (trie membership proofs, MMR/BEEFY multi-proofs, ECDSA/BLS recovery, etc.) — against an attacker-supplied `Vec<Message>` before any weight or fee is charged. [1](#0-0) 

The same unauthenticated pattern exists in `pallet-state-coprocessor`, whose `validate_unsigned` also runs full proof verification (`Self::handle_get_requests(message.clone())`) directly on caller-supplied data before returning validity. [2](#0-1) 

### Finding Description
Substrate's transaction pool calls `ValidateUnsigned::validate_unsigned` on *every node* that receives a gossiped unsigned extrinsic — before block inclusion, before weight metering, and before any fee is charged (this is the whole point of `handle_unsigned`, documented as "free" execution). Because `validate_unsigned` for `pallet_ismp::Call::handle_unsigned` unconditionally calls `Self::execute(messages.clone())`, an attacker can submit a `Vec<Message>` whose size and content are entirely under their control — e.g., many `Message::Request` or `Message::Response` entries, each carrying storage/MMR/consensus proofs that must be cryptographically verified (BEEFY multi-signature recovery, MMR proof verification, RLP/trie membership checks, EVM/Substrate state-proof verification) — and force every node that relays or validates the transaction to perform this expensive work repeatedly, for free, with no upfront gate on the number of messages, the number of requests/keys per message, or the size of the embedded proofs.

This mirrors the BentoML bug class precisely: an unauthenticated endpoint that keeps performing increasing amounts of work per attacker-supplied unit (there: boundary dashes character-by-character; here: proof items/messages in a batch) with no bound check before the expensive processing starts. The pallet's own documentation acknowledges the free-execution design relies entirely on validity-checking being cheap ("Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing"), but the check itself *is* the expensive full-verification path, not a cheap pre-filter. [3](#0-2) 

Other pallets in the same codebase that reuse the unsigned-mempool pattern already carry explicit defenses against exactly this kind of pre-fee-gate abuse — e.g. `pallet-call-decompressor` was hardened specifically because its unsigned mempool path let "a fee-less attacker … have a tiny zstd 'bomb' expanded to gigabytes during transaction-pool validation, before any size check," and the fix added a bound *before* the expensive work in the shared `decompress` choke point. [4](#0-3) 

`pallet-ismp` and `pallet-state-coprocessor`'s `validate_unsigned` implementations have no analogous upfront bound on `messages.len()`, `requests.len()`, or per-request `keys.len()` before invoking full proof verification. [5](#0-4) [6](#0-5) 

### Impact Explanation
Any unprivileged network participant able to submit or gossip an extrinsic (message dispatcher / relayer-equivalent — no signature or fee required by design) can craft a `handle_unsigned` call with a large batch of messages/requests each carrying maximal but syntactically valid proof data, forcing every full node in the network to repeatedly run expensive cryptographic verification (MMR, BEEFY multi-signature ECDSA recovery, trie/state proofs) for free, on every re-broadcast/re-validation cycle. This is a network-wide CPU/availability degradation vector reachable from a single dispatched, unsigned message — matching the "route unable to deliver messages" / DoS criteria for a valid High-severity finding, since sustained abuse can starve nodes' transaction-pool validation capacity and delay legitimate message delivery across the bridge.

### Likelihood Explanation
High. The attack requires no privileges, no signature, and no fee — it is the intended free/unauthenticated path for relayers, and the only defense is the substrate node's default extrinsic-size cap (which bounds raw bytes but not the cost-per-byte of cryptographic verification the SCALE-decoded batch triggers). Nothing in `pallet_ismp::validate_unsigned` or `pallet_state_coprocessor::validate_unsigned` caps the number of messages, requests, or keys before calling into full execution/proof verification.

### Recommendation
Add an explicit, cheap upfront bound in both `validate_unsigned` implementations — on `messages.len()` for `pallet-ismp` and on `requests.len()` / total keys for `pallet-state-coprocessor` — rejecting oversized batches with `InvalidTransaction::Call`/`ExhaustsResources` *before* calling `Self::execute` / `Self::handle_get_requests`, mirroring the fix already applied in `pallet-call-decompressor::decompress` (bound-before-work at the single choke point every caller flows through).

### Proof of Concept
1. Construct a `pallet_ismp::Call::handle_unsigned` extrinsic with `messages: Vec<Message>` containing hundreds/thousands of `Message::Request` entries, each with a maximally-sized (but validly shaped) storage/MMR proof.
2. Submit as an unsigned extrinsic via RPC to any node; it propagates to peers via gossip.
3. Every receiving node's transaction pool invokes `validate_unsigned`, which calls `Self::execute(messages.clone())`, running full proof verification for the entire batch — with no fee paid and no upfront size/cost gate, as shown in `modules/pallets/ismp/src/lib.rs:614-626`.
4. Repeating/resubmitting variants (bypassing the `provides`-tag dedup by trivially varying proof padding) sustains the load across the network's validating nodes.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L604-626)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T> {
		type Call = Call<T>;

		// empty pre-dispatch do we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

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

**File:** modules/pallets/state-coprocessor/src/lib.rs (L107-129)
```rust
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T>
	where
		T::AccountId: AsRef<[u8]>,
		<T as frame_system::Config>::AccountId: From<[u8; 32]>,
		<T as pallet_ismp::Config>::Balance: Into<u128>,
	{
		type Call = Call<T>;

		// empty pre-dispatch so we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let Call::handle_unsigned { message } = call else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};

			if let Err(err) = Self::handle_get_requests(message.clone()) {
				log::error!(target: "ismp", "{:?}", err);
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L220-232)
```rust
	pub fn decompress(
		compressed_bytes: Vec<u8>,
		encoded_call_size: u32,
	) -> Result<Vec<u8>, DispatchError> {
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);

```
