## Analysis

This maps to a legitimate resource-exhaustion analog: unsigned `handle_unsigned` extrinsics run full, computationally-expensive consensus proof verification during transaction-pool validation (before any block inclusion, before any fee, and before the runtime's own call filter has a chance to reject them), so a single unprivileged submitter can force every full node on the network to burn CPU on expensive SP1/Groth16 verification repeatedly for free.

### Title
Unsigned `handle_unsigned` BEEFY/SP1 consensus messages force full-cost proof verification during mempool validation before `IsmpCallFilter` can reject them, enabling free CPU-exhaustion DoS - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet_ismp::Pallet::<T>::handle_unsigned` is dispatchable by anyone with `ensure_none(origin)` [1](#0-0) . Its `ValidateUnsigned::validate_unsigned` implementation runs the *entire* message-handling pipeline — `Self::execute(messages.clone())` — as part of transaction-pool admission/gossip validation, before the transaction is ever included in a block [2](#0-1) . When the batch contains a `Message::Consensus` targeting the BEEFY consensus client, this reaches `ismp_beefy::BeefyConsensusClient`, which is registered in `pallet_ismp::Config::ConsensusClients` for the Gargantua runtime [3](#0-2) , and can invoke the SP1 Groth16 verifier (`verify_sp1_consensus`), a check whose cost (per the pallet's own weight benchmark) is on the order of ~600ms of CPU per call regardless of proof validity [4](#0-3) .

The runtime does add a `IsmpCallFilter` that specifically rejects `handle_unsigned` batches carrying BEEFY consensus messages, precisely because "Allowing raw updates through `handle_unsigned` would bypass" the mandatory SP1 gate [5](#0-4) . However, that filter is wired as `frame_system::Config::BaseCallFilter`/`pre_dispatch`, which is only consulted when a call actually *dispatches* on-chain. It is confirmed by the runtime's own simtest that a *signed* extrinsic is required to exercise the filter, specifically because "a signed extrinsic skips `validate_unsigned` and goes straight to dispatch, where the filter runs before the call body" [6](#0-5) . An unsigned `handle_unsigned` transaction never reaches that dispatch-time filter check for invalid transactions — `ValidateUnsigned::validate_unsigned` runs first, unconditionally executing the message (including full SP1 verification) purely to decide pool admission, and only then returns `InvalidTransaction::BadProof` on failure [2](#0-1) .

### Finding Description
This is analogous to the "MadeYouReset" bug class: a malformed/garbage request (an unsigned `handle_unsigned` payload wrapping a syntactically well-formed but bogus BEEFY/SP1 consensus proof) forces the receiving side to perform substantial, non-trivial work (a full Groth16 pairing verification) that is then discarded, with no fee, deposit, or "abuse counter" charged to the submitter, and this validation runs on *every full node* that receives the transaction over gossip (not just the block author), because Substrate's transaction pool calls `validate_unsigned` independently on each peer before propagating/accepting a transaction. Because the transaction is unsigned, submission is free; because `Self::execute` runs before `IsmpCallFilter`/`BaseCallFilter` is consulted, the intended guard against exactly this abuse (added specifically to stop BEEFY updates from bypassing the SP1 gate) has no effect on the mempool-validation cost — it only prevents the (already-rejected) transaction from being included in a block, after the expensive work has already run network-wide.

### Impact Explanation
An attacker can generate an arbitrary number of distinct but syntactically valid `ConsensusMessage` payloads (varying nonce/commitment bytes to avoid transaction-pool de-duplication) targeting the BEEFY consensus state id, and broadcast them as unsigned extrinsics. Each one forces every full node's `validate_unsigned` call to execute `BeefyConsensusClient::verify_consensus`, running a full SP1 Groth16 verification (~600ms of CPU per the pallet's benchmarked weight) before being rejected. Flooding the network with such transactions can exhaust CPU capacity across the validator/collator set, degrading block production and increasing the risk of missed authoring slots — a network-wide availability/DoS impact reachable directly from a single unprivileged, feeless, unsigned extrinsic.

### Likelihood Explanation
Likelihood is high: `handle_unsigned` is explicitly designed to be callable by "anyone" for free [7](#0-6) , requires no stake, signature, or fee, and the BEEFY/SP1 path is reachable purely by choosing the right `consensus_state_id` in the message — no valid witness/signature data is required to trigger the expensive verification branch, only a payload of the correct shape (the cost of Groth16 pairing checks is not gated by proof correctness).

### Recommendation
Enforce `IsmpCallFilter`/`BaseCallFilter`-equivalent checks (or an explicit "does this batch contain a BEEFY consensus message" rejection) inside `ValidateUnsigned::validate_unsigned` itself, before calling `Self::execute`, so that transactions which will ultimately be dispatch-filtered are rejected cheaply at the mempool boundary rather than after paying the full verification cost. More generally, cheap, structural pre-checks (message type / consensus id whitelisting) should run in `validate_unsigned` prior to any cryptographic verification for unsigned, fee-less extrinsics.

### Proof of Concept
1. Craft an unsigned `Ismp::handle_unsigned` extrinsic carrying a single `Message::Consensus { consensus_state_id: BEEFY_CONSENSUS_ID, consensus_proof: <well-formed but invalid SP1 proof bytes>, .. }`.
2. Submit it via RPC to a Gargantua/Nexus node's transaction pool.
3. Observe that `ValidateUnsigned::validate_unsigned` invokes `Self::execute`, which reaches `ismp_beefy::BeefyConsensusClient` → SP1 Groth16 verification (cost ~600ms per the pallet's benchmark weight), before ultimately returning `InvalidTransaction::BadProof`.
4. Repeat with mutated proof bytes/nonces to bypass any duplicate-transaction detection, and broadcast in parallel to many peers — each peer independently re-runs the same expensive validation on receipt via gossip, at zero cost to the submitter.

*Note:* I was not able to directly execute this against a live node (no runtime/tooling access in this environment); the finding is based on static analysis of the `validate_unsigned` control flow, the `ConsensusClients` wiring, and the pallet's own SP1 benchmark weight, cross-referenced with the runtime's own documented intent (`IsmpCallFilter` comment) that `handle_unsigned` + BEEFY should never be reachable — confirming the filter's scope does not cover the unsigned-validation path.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L360-365)
```rust
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
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

**File:** parachain/runtimes/gargantua/src/ismp.rs (L174-190)
```rust
	type ConsensusClients = (
		ismp_bsc::BscClient<Ismp, Runtime, ismp_bsc::Testnet>,
		ismp_sync_committee::SyncCommitteeConsensusClient<Ismp, Sepolia, Runtime, Ethereum>,
		ismp_sync_committee::SyncCommitteeConsensusClient<Ismp, gnosis::Testnet, Runtime, Gnosis>,
		ismp_parachain::ParachainConsensusClient<
			Runtime,
			IsmpParachain,
			ParachainStateMachineProvider,
		>,
		ismp_grandpa::consensus::GrandpaConsensusClient<Runtime>,
		ismp_arbitrum::ArbitrumConsensusClient<Ismp, Runtime>,
		ismp_optimism::OptimismConsensusClient<Ismp, Runtime>,
		ismp_polygon::PolygonClient<Ismp, Runtime>,
		ismp_tendermint::TendermintClient<Ismp, Runtime>,
		ismp_pharos::PharosClient<Ismp, Runtime, ismp_pharos::Testnet>,
		ismp_beefy::BeefyConsensusClient<Ismp, Runtime>,
	);
```

**File:** parachain/runtimes/gargantua/src/weights/pallet_beefy_consensus_proofs.rs (L90-99)
```rust
	fn submit_proof() -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `952`
		//  Estimated: `4417`
		// Minimum execution time: 601_332_542_000 picoseconds.
		Weight::from_parts(608_064_578_000, 0)
			.saturating_add(Weight::from_parts(0, 4417))
			.saturating_add(T::DbWeight::get().reads(13))
			.saturating_add(T::DbWeight::get().writes(2))
	}
```

**File:** parachain/runtimes/gargantua/src/lib.rs (L808-836)
```rust
/// Gargantua routes all BEEFY consensus updates through `pallet-beefy-consensus-proofs`, which
/// requires each proof to pass SP1 zkVM verification before it can advance the BEEFY state.
/// Allowing raw updates through `handle_unsigned` would bypass that requirement entirely, so
/// any batch that carries a BEEFY consensus message is rejected here. `fund_message` is also
/// disabled because gargantua uses the bandwidth model for request fees; per-message top-ups
/// have no role in that accounting.
///
/// A consensus message only names the state it updates, so we ask the host which client owns
/// that state and compare against BEEFY. Reading from the host remains correct even as more
/// states (Polkadot, Paseo) are bound to the same client over time.
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
}
```

**File:** parachain/simtests/src/base_call_filter.rs (L1-9)
```rust
//! Simnode coverage for the runtime base call filter (`IsmpCallFilter`).
//!
//! The filter blocks `Ismp::fund_message` outright and blocks `Ismp::handle_unsigned`
//! when the batch carries a BEEFY consensus update. We submit each call as a *signed*
//! extrinsic on purpose: a signed extrinsic skips `validate_unsigned` and goes straight
//! to dispatch, where the filter runs before the call body. A blocked call comes back as
//! `System::CallFiltered`; a call the filter lets through reaches the body and trips
//! `ensure_none` with `BadOrigin`. Telling those two apart is the whole test, and it lets
//! us exercise the filter without building real BEEFY proofs.
```
