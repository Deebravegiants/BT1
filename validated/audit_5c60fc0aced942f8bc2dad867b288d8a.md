## Title
Unbounded free unsigned `handle_unsigned` extrinsic enables algorithmic-complexity CPU-consumption DoS via oversized message batches - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic accepts an attacker-controlled `Vec<Message>` and is charged a **static, size-independent weight** (`Weight::from_parts(300_000_000, 0)`), while `ValidateUnsigned::validate_unsigned` fully **executes** the entire batch (`Self::execute(messages.clone())`) for free, on every node's transaction-pool validation path, before the extrinsic is ever included in a block. This is directly analogous to CVE-2022-40188: an unprivileged party can submit "large sets" (many messages, many requests per message, or consensus proofs carrying large header/ancestry/signature sets) that are processed with real, unbounded computational cost, but the protocol treats the cost as constant/free — an algorithmic-complexity denial-of-service.

### Finding Description
`handle_unsigned` is declared with:
```rust
#[pallet::weight(weight())]
#[pallet::call_index(0)]
#[frame_support::transactional]
pub fn handle_unsigned(origin: OriginFor<T>, messages: Vec<Message>) -> DispatchResultWithPostInfo {
    ensure_none(origin)?;
    Self::execute(messages.clone())?;
    Ok(().into())
}
``` [1](#0-0) 

with the "static weight" comment explicitly acknowledging the weight does not reflect actual cost:
```rust
/// Static weights because these should get overridden by the FeeHandler
fn weight() -> Weight {
    Weight::from_parts(300_000_000, 0)
}
``` [2](#0-1) 

Crucially, `ValidateUnsigned::validate_unsigned` — which runs on **every node**, for every transaction seen in gossip, before it's ever charged a fee or included in a block — executes the entire message batch:
```rust
fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
    let messages = match call {
        Call::handle_unsigned { messages } => messages,
        ...
    };
    let events = Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;
    ...
}
``` [3](#0-2) 

`Self::execute` iterates every message and calls `handle_incoming_message`, which dispatches consensus updates, request/response/timeout handling — including full storage-proof verification, header-ancestry walks, and (for non-BEEFY consensus clients) signature-set verification:
```rust
let message_results = messages
    .iter()
    .map(|msg| handle_incoming_message(&host, msg.clone()))
    .collect::<Result<Vec<_>, _>>()...
``` [4](#0-3) 

There is no bound on: (1) the number of `Message`s in the `Vec<Message>`, (2) the number of `PostRequest`s inside a single `RequestMessage`, or (3) the size of nested proof structures (e.g. GRANDPA header ancestries, BSC epoch ancestries, parachain header proofs) carried inside a `Message::Consensus`. For example, the GRANDPA prover/verifier walks an entire submitted header ancestry chain and verifies justifications over it — cost scales with the number of headers supplied, not with any weight charged: [5](#0-4) 

The BSC verifier similarly loops over an attacker-supplied `epoch_header_ancestry` recomputing hashes for every header: [6](#0-5) 

Docs confirm the design intent — this is meant to be "free" and rely solely on mempool validity checks for spam protection, exactly the assumption CVE-2022-40188 broke for Knot Resolver:
> "Pallet ISMP uses unsigned transactions for executing cross-chain messages... executed for free as unsigned transactions... This validity check ensures that the transaction can be successfully executed and contains valid proofs." [7](#0-6) 

Note that production runtimes (`gargantua`, `nexus`) do filter out `Message::Consensus` batches bound to the BEEFY consensus client from `handle_unsigned`, forcing BEEFY through the SP1-gated `pallet-beefy-consensus-proofs` path: [8](#0-7) 
However, this filter does **not** restrict the size/number of `Message::Request`, `Message::Response`, `Message::Timeout`, or non-BEEFY `Message::Consensus` (GRANDPA, parachain, BSC, tendermint, pharos, etc.) entries, nor does it bound the number of messages in the batch or requests within a message.

### Impact Explanation
Because `handle_unsigned` is an unsigned, fee-less extrinsic whose declared weight is a fixed constant regardless of payload size, and because the entire payload is executed during `validate_unsigned` on every full node (mempool gossip validation, run before any block inclusion or fee is charged), an attacker can craft a single transaction containing a large `Vec<Message>` (many requests, or consensus messages with large header ancestries/signature sets) that costs disproportionately more CPU time to validate than the fixed weight accounted for. Submitting/gossiping many such transactions can degrade or stall block production and transaction-pool processing across the network — a CPU-consumption denial-of-service, matching the CVSS 7.5 (Availability: High) profile of CVE-2022-40188.

### Likelihood Explanation
High: any unprivileged relayer/message-dispatcher can submit `handle_unsigned` extrinsics — no signature, fee, or authorization is required (`ensure_none(origin)`), and the transaction pool itself performs the expensive validation on receipt.

### Recommendation
- Make the extrinsic's declared weight proportional to the actual content size (number of messages, requests per message, header/ancestry counts, signature counts) rather than a fixed constant, so `pallet_transaction_payment`/block weight limits properly reject oversized batches before execution.
- Enforce hard bounds (e.g., `BoundedVec` with a `MaxMessages`/`MaxRequestsPerMessage`/`MaxAncestryLength` config) on all attacker-supplied collections reachable through `handle_unsigned` before any cryptographic or proof verification work begins.
- Consider cheap upfront size/shape validation in `validate_unsigned` prior to invoking `Self::execute`, so oversized or degenerate batches are rejected before the expensive verification path runs.

### Proof of Concept
1. Construct a `pallet_ismp::Call::handle_unsigned` extrinsic with a `Vec<Message>` containing, e.g., a single `Message::Consensus` whose proof is a GRANDPA `FinalityProof` with `unknown_headers` set to the maximum number of headers permitted by extrinsic size limits (thousands of headers), or a `Message::Request` with an extremely large `Vec<PostRequest>`.
2. Submit as an unsigned transaction (`create_unsigned`) — no signer, no fee required, matching the pattern used in `parachain/simtests/src/pallet_ismp.rs`.
3. Because `ValidateUnsigned::validate_unsigned` calls `Self::execute(messages.clone())` directly, every node relaying the transaction fully executes the ancestry walk / request-batch handling at mempool-validation time, while the extrinsic's accounted weight remains the fixed `Weight::from_parts(300_000_000, 0)`.
4. Repeating this with multiple crafted transactions (each producing a unique `provides` tag to avoid pool dedup) causes sustained CPU consumption across the network's mempool/gossip layer, independent of block inclusion.

### Citations

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

**File:** modules/pallets/ismp/src/lib.rs (L727-730)
```rust
	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```

**File:** modules/pallets/ismp/src/impls.rs (L43-51)
```rust
		let message_results = messages
			.iter()
			.map(|msg| handle_incoming_message(&host, msg.clone()))
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;
```

**File:** modules/consensus/grandpa/prover/src/lib.rs (L246-270)
```rust
		let mut unknown_headers = vec![];
		let pb = ProgressBar::new(diff as u64);
		for height in previous_finalized_height..=max_height {
			let current_hash = self
				.rpc
				.chain_get_block_hash(Some(height.into()))
				.await?
				.ok_or_else(|| anyhow!("Failed to fetch block hash for height {height}"))?;
			let header = self
				.rpc
				.chain_get_header(Some(current_hash))
				.await?
				.ok_or_else(|| anyhow!("Header with hash: {current_hash:?} not found!"))?;
			let sp_runtime_header = DefaultHeader::decode(&mut header.encode().as_ref())?;
			unknown_headers.push(sp_runtime_header.clone());

			if let Some(_) = find_scheduled_change(&sp_runtime_header) {
				log::trace!(
					"Found set rotation for {} at block number {height:?}",
					self.options.state_machine
				);
				if height != previous_finalized_height {
					target_block_hash = Some(current_hash);
					// stop here
					break;
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L156-162)
```rust
            let mut parent_hash = Header::from(&update.epoch_header_ancestry[0]).hash::<H>();
            for header in update.epoch_header_ancestry[1..].into_iter() {
                if parent_hash != header.parent_hash {
                    Err(Error::InvalidEpochAncestry)?
                }
                parent_hash = Header::from(header).hash::<H>()
            }
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** parachain/runtimes/gargantua/src/lib.rs (L818-835)
```rust
pub struct IsmpCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for IsmpCallFilter {
	fn contains(call: &RuntimeCall) -> bool {
		use ::ismp::{host::IsmpHost, messaging::Message};
		match call {
			RuntimeCall::Ismp(pallet_ismp::Call::fund_message { .. }) => false,
			RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned { messages }) => {
				let host = Ismp::default();
				!messages.iter().any(|message| match message {
					Message::Consensus(consensus) =>
						host.consensus_client_id(consensus.consensus_state_id) ==
							Some(ismp_beefy::BEEFY_CONSENSUS_ID),
					_ => false,
				})
			},
			_ => true,
		}
	}
```
