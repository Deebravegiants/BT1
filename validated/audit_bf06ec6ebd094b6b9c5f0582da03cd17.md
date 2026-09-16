### Title
Unbounded BEEFY signature vector lets a free, unauthenticated `handle_unsigned` extrinsic force unbounded ECDSA-recovery work - ([File: modules/consensus/beefy/verifier/src/lib.rs])

### Summary
`pallet-ismp`'s `handle_unsigned` call accepts unsigned, fee-less `Message::Consensus` extrinsics from any peer and validates them for free inside `ValidateUnsigned::validate_unsigned`, which runs the full BEEFY consensus verification path before any economic cost is charged. [1](#0-0)  Inside `verify_mmr_update_proof`, the number of ECDSA signature-recovery operations performed is `mmr.signed_commitment.signatures.len()` — a value fully controlled by the submitter — with only a lower-bound "supermajority" check and no upper bound on how many (even garbage) signature entries can be included. [2](#0-1)  This mirrors the JLine3 NAWS bug class: an unauthenticated, essentially cost-free network input triggers repeated expensive server-side computation (there, terminal redraws; here, `secp256k1_recover`) with only a minimum-bound check and no maximum bound.

### Finding Description
- `handle_unsigned` is dispatched with `ensure_none(origin)` — no signature, no fee — and calls `Self::execute(messages.clone())`. [3](#0-2) 
- The same execution runs a second time (for free) inside `validate_unsigned`, which every full node performs on every unsigned extrinsic it receives via gossip, before the extrinsic is even included in a block. [4](#0-3) 
- `verify_mmr_update_proof` reads `signatures_length = mmr.signed_commitment.signatures.len()` and only checks `check_participation_threshold(signatures_length, authority_set.len)` — a lower-bound "at least supermajority" gate — before iterating over **every** entry in `signatures` and calling the expensive `H::secp256k1_recover` (ECDSA public-key recovery) for each one. [5](#0-4)  There is no code path that rejects `signatures.len()` for being *too large* relative to the actual authority set size (`authority_set.len`), so an attacker can submit far more entries than the authority set has members — all garbage signatures that will fail recovery/verification only after every one has been processed.
- The call's declared weight is a fixed constant, `Weight::from_parts(300_000_000, 0)`, independent of message contents, so the runtime's weight accounting does not scale with (and therefore does not deter) an arbitrarily large `signatures` vector. [6](#0-5) 
- The only practical ceiling on `signatures.len()` is the extrinsic/block byte-size limit (`RuntimeBlockLength`, e.g. 5MB with 75% for normal-class extrinsics on gargantua, or up to 8MB/85% recommended for GRANDPA-heavy solochains). [7](#0-6) [8](#0-7)  At roughly 68 bytes per vote entry (index + 65-byte signature), several megabytes of block/extrinsic space is enough to pack tens of thousands of forged "signatures," each of which costs a full secp256k1 recovery before the proof is ultimately rejected (e.g., at the authority-membership Merkle-multi-proof check).

### Impact Explanation
Because `handle_unsigned` is unsigned and free, and `validate_unsigned` performs the same expensive verification before block inclusion is even attempted, an unauthenticated attacker can force every relaying/validating node in the network to repeatedly perform tens of thousands of ECDSA recoveries per submitted message, with no fee paid and no upper bound enforced on the signature-vector length. This is a CPU-exhaustion Denial-of-Service against Hyperbridge's BEEFY consensus-message ingestion path (mempool validation + `Self::execute`), directly analogous to the JLine3 NAWS finding: an unauthenticated, unbounded-count numeric input drives an expensive per-item loop that is only lower-bounded, never upper-bounded. Because this pathway underlies consensus-state updates that gate all cross-chain message delivery, degrading it can stall the delivery of legitimate requests/responses network-wide (a "route unable to deliver messages" condition), which is why this reaches the required severity/impact bar.

### Likelihood Explanation
High. The attack requires only crafting an unsigned extrinsic containing a `Message::Consensus` whose BEEFY proof carries an oversized `signatures` vector; no keys, no authority set membership, no fee, and no prior state are required to reach the expensive loop — the vector length is checked only for a lower bound before the recovery loop runs. Any node processing pool-gossip traffic executes `validate_unsigned` and is exposed.

### Recommendation
- Enforce a hard upper bound on `mmr.signed_commitment.signatures.len()` (and the corresponding `votes.length` in `EcdsaBeefy.sol`) relative to the known/trusted `authority_set.len`, rejecting proofs whose signature count exceeds this bound before performing any `secp256k1_recover` calls.
- Make the declared extrinsic weight for `handle_unsigned` (and/or the BEEFY-specific execution path) scale with the actual number of signatures/messages being processed rather than remaining a fixed constant, so weight accounting reflects real computational cost.
- Consider deduplicating/sorting `authority_indices` and short-circuiting once enough valid, distinct-index recoveries have been gathered to satisfy the supermajority threshold, rather than unconditionally processing the entire vector.

### Proof of Concept
1. Construct a `ConsensusMessage` whose `consensus_proof` SCALE-encodes an `MmrProof` with a `signed_commitment.signatures` vector containing, e.g., 50,000 entries of `{index: i, signature: [0u8; 65]}` (all garbage/invalid signatures), sized to fit within the runtime's `RuntimeBlockLength` normal-class limit.
2. Wrap it as `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Consensus(consensus_message)] }` and submit as an unsigned extrinsic.
3. Every node that receives the extrinsic via gossip invokes `ValidateUnsigned::validate_unsigned`, which calls `Self::execute`, which calls into `verify_mmr_update_proof`, which performs `secp256k1_recover` 50,000 times before the proof is finally rejected at the authority Merkle-multi-proof check.
4. Repeating this from multiple unauthenticated peers with distinct nonce/salted bytes (to avoid `provides`-tag dedup in the tx pool) causes sustained CPU load across the network's validating nodes at negligible cost to the attacker.

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

**File:** modules/pallets/ismp/src/lib.rs (L604-625)
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

**File:** modules/pallets/ismp/src/lib.rs (L727-730)
```rust
	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-162)
```rust
pub fn verify_mmr_update_proof<H: Keccak256 + EcdsaRecover + Send + Sync>(
	mut trusted_state: ConsensusState,
	mmr: MmrProof,
) -> Result<(ConsensusState, H256), Error> {
	let signatures_length = mmr.signed_commitment.signatures.len();
	let latest_height = mmr.signed_commitment.commitment.block_number;

	if trusted_state.latest_beefy_height >= latest_height {
		return Err(Error::StaleHeight {
			trusted_height: trusted_state.latest_beefy_height,
			current_height: latest_height,
		});
	}

	let commitment = mmr.signed_commitment.commitment.clone();

	// Pick the authority set the commitment claims to be signed under, then judge
	// participation against that set alone.
	let authority_set = if commitment.validator_set_id == trusted_state.current_authorities.id {
		&trusted_state.current_authorities
	} else if commitment.validator_set_id == trusted_state.next_authorities.id {
		&trusted_state.next_authorities
	} else {
		return Err(Error::UnknownAuthoritySet { id: commitment.validator_set_id });
	};

	if !check_participation_threshold(signatures_length as u32, authority_set.len) {
		return Err(Error::SuperMajorityRequired);
	}

	let mmr_root_data = commitment
		.payload
		.get_raw(&MMR_ROOT_PAYLOAD_ID)
		.ok_or(Error::MmrRootHashMissing)?;

	if mmr_root_data.len() != 32 {
		return Err(Error::InvalidMmrRootHashLength { len: mmr_root_data.len() });
	}
	let mmr_root = H256::from_slice(mmr_root_data);

	let commitment_hash = H::keccak256(&commitment.encode());
	let mut authority_leaves: Vec<[u8; 32]> = Vec::new();
	let mut authority_indices = Vec::new();

	for sig in mmr.signed_commitment.signatures.iter() {
		let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)
			.map_err(|_| Error::FailedToRecoverPublicKey)?;

		let hashed_uncompressed = H::keccak256(&uncompressed);

		let mut eth_address = [0u8; 20];
		eth_address.copy_from_slice(&hashed_uncompressed.as_ref()[12..]);

		let authority_address_hash = H::keccak256(&eth_address);

		authority_leaves.push(authority_address_hash.into());
		authority_indices.push(sig.index as usize);
	}
```

**File:** parachain/runtimes/gargantua/src/lib.rs (L316-344)
```rust
parameter_types! {
	pub const Version: RuntimeVersion = VERSION;

	// This part is copied from Substrate's `bin/node/runtime/src/lib.rs`.
	//  The `RuntimeBlockLength` and `RuntimeBlockWeights` exist here because the
	// `DeletionWeightLimit` and `DeletionQueueDepth` depend on those to parameterize
	// the lazy contract deletion.
	pub RuntimeBlockLength: BlockLength =
		BlockLength::max_with_normal_ratio(5 * 1024 * 1024, NORMAL_DISPATCH_RATIO);
	pub RuntimeBlockWeights: BlockWeights = BlockWeights::builder()
		.base_block(BlockExecutionWeight::get())
		.for_class(DispatchClass::all(), |weights| {
			weights.base_extrinsic = ExtrinsicBaseWeight::get();
		})
		.for_class(DispatchClass::Normal, |weights| {
			weights.max_total = Some(NORMAL_DISPATCH_RATIO * MAXIMUM_BLOCK_WEIGHT);
		})
		.for_class(DispatchClass::Operational, |weights| {
			weights.max_total = Some(MAXIMUM_BLOCK_WEIGHT);
			// Operational transactions have some extra reserved space, so that they
			// are included even if block reached `MAXIMUM_BLOCK_WEIGHT`.
			weights.reserved = Some(
				MAXIMUM_BLOCK_WEIGHT - NORMAL_DISPATCH_RATIO * MAXIMUM_BLOCK_WEIGHT
			);
		})
		.avg_block_initialization(AVERAGE_ON_INITIALIZE_RATIO)
		.build_or_panic();
	pub const SS58Prefix: u16 = 0;
}
```

**File:** docs/content/developers/polkadot/solochains.mdx (L15-22)
```text
In your runtime, you should configure Hyperbridge as the coprocessor and add a GRANDPA consensus client to the list of consensus clients. The host state machine should be assigned a unique value for each solochain connected to Hyperbridge. You should also configure a larger block length limit to accommodate for large GRANDPA proofs. The new recommended limit is `8MB`, with a maximum extrinsic limit of 85%.

Every other configuration detail remains unchanged as described in the previous sections

```rust showLineNumbers [runtime.rs]

pub RuntimeBlockLength: BlockLength =
    BlockLength::max_with_normal_ratio(8 * 1024 * 1024, Perbill::from_percent(85));
```
