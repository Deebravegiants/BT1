### Title
Fixed generalized Merkle indices in the Ethereum sync-committee light client break across BeaconState schema-changing forks - ([File: modules/consensus/sync-committee/verifier/src/lib.rs])

### Summary
The Ethereum sync-committee consensus client verifies `finalized_header`, `execution_payload`, and `next_sync_committee` Merkle branches against **hard-coded generalized indices and tree depths** (`FINALIZED_ROOT_INDEX`/`_LOG2`, `EXECUTION_PAYLOAD_INDEX`/`_LOG2`, `NEXT_SYNC_COMMITTEE_INDEX`/`_LOG2`, `EXECUTION_PAYLOAD_STATE_ROOT_INDEX`, `EXECUTION_PAYLOAD_BLOCK_NUMBER_INDEX`, `EXECUTION_PAYLOAD_TIMESTAMP_INDEX`) that are fixed per network in `Config`. These indices encode the position/depth of fields inside the SSZ-merkleized `BeaconState`/`ExecutionPayload` containers. Ethereum hard forks (Capella, Deneb, Electra, Fulu) repeatedly add fields to these containers, which shifts field indices and can cross power-of-two boundaries that change the required Merkle tree height — exactly the bug class described in the EigenLayer `BeaconChainProofs.verifyWithdrawal()` report. The verifier never branches on the fork/epoch of the header being proven to pick the matching indices/height for that specific fork era; it always uses the single set of indices baked into `Config` for the whole network.

### Finding Description
`verify_sync_committee_attestation` in [1](#0-0)  calls `is_valid_merkle_branch` three times, each time using a fixed `C::FINALIZED_ROOT_INDEX_LOG2`/`C::FINALIZED_ROOT_INDEX`, `C::EXECUTION_PAYLOAD_INDEX_LOG2`/`C::EXECUTION_PAYLOAD_INDEX`, or `C::NEXT_SYNC_COMMITTEE_INDEX_LOG2`/`C::NEXT_SYNC_COMMITTEE_INDEX` from the `Config` trait implementation for the target network (e.g. mainnet), regardless of which fork era the `update.finalized_header`/`update.attested_header` slot actually belongs to.

These constants are defined once per network in [2](#0-1)  and instantiated with single fixed values per chain, e.g. for mainnet: [3](#0-2) . The `Config` trait does carry separate fork epoch/version constants (`CAPELLA_FORK_EPOCH`, `DENEB_FORK_EPOCH`, `ELECTRA_FORK_EPOCH`, `FULU_FORK_EPOCH`, etc.) but these are only consumed by `compute_fork_version`/domain computation for the BLS signature check — never to select a fork-appropriate generalized index or tree depth for the Merkle proofs.

This is structurally the same root cause as the reported EigenPod bug: the number of fields in `BeaconState` (and `ExecutionPayload`) is not constant across forks — Capella, Deneb, and Electra each add new top-level fields to `BeaconState` (Electra alone adds ~9 fields for the pending deposits/withdrawals/consolidations queues), which can push the field count across a power-of-two boundary and increase the tree height/generalized index needed to prove membership of `latest_execution_payload_header`, sync committees, or the finality checkpoint inside `BeaconState`. A verifier that hard-codes one depth for the whole chain either:
1. Rejects legitimate proofs from a differently-schemad fork era (breaking valid state updates / consensus progression), or
2. Accepts a Merkle branch of the wrong depth against the wrong generalized index — since `is_valid_merkle_branch` only walks `branch.len()` (`_LOG2`) layers up using the supplied sibling hashes and never independently re-derives the expected tree height from the container's actual schema, a mismatched, attacker-influenced depth/index pair can be used to fabricate/forge a Merkle path (the same class of second-preimage risk called out in the report and explicitly documented in this repo's own Merkle-tree design doc: [4](#0-3) ).

### Impact Explanation
`verify_sync_committee_attestation` is the core consensus-verification entry point for the Ethereum (and Gnosis) light client that Hyperbridge relies on to establish/advance the trusted `VerifierState` (finalized header, sync committees, state roots) used to authenticate all subsequent ISMP request/response state proofs originating from these state machines. A forged or de-synced consensus update here would let an attacker either:
- Falsely accept a forged finalized-header/execution-payload/sync-committee Merkle branch (unsound state commitment → forged message delivery for any ISMP messages later proven against that state root), or
- Permanently break the ability of the relayer network to advance trusted state across a fork boundary that changes container field counts (a route unable to deliver messages), since a legitimate proof generated for the post-fork schema will be verified with pre-fork indices (or vice versa) and rejected.

### Likelihood Explanation
The mismatch is guaranteed to occur whenever a hard fork that changes `BeaconState`/`ExecutionPayload` field counts happens while the trusted client continues to track the chain — this is a normal, expected, non-adversarial event (Capella, Deneb, and Electra have already occurred on mainnet; more forks are scheduled). No governance/admin/peer compromise is required — any relayer submitting a legitimate consensus update spanning the fork boundary triggers it, and a malicious relayer/message dispatcher could specifically exploit the fixed-depth branch verification to attempt to inject a forged branch once a depth mismatch exists.

### Recommendation
Do not hard-code a single generalized index/tree-depth per network. Instead, determine the applicable `BeaconState`/`ExecutionPayload` schema (and therefore the correct generalized indices and `_LOG2` depths for `FINALIZED_ROOT_INDEX`, `EXECUTION_PAYLOAD_INDEX`, `NEXT_SYNC_COMMITTEE_INDEX`, and the execution-payload multi-proof indices) based on the fork epoch that the header/state being proven actually belongs to (comparing `update.finalized_header`/`attested_header` slot's epoch against `CAPELLA_FORK_EPOCH`/`DENEB_FORK_EPOCH`/`ELECTRA_FORK_EPOCH`/`FULU_FORK_EPOCH`), mirroring the fix applied to `BeaconChainProofs.verifyWithdrawal()` referenced in the report (PRs polytope-labs equivalents to eigenlayer #395/#416): store per-fork constant sets and select the correct one at verification time rather than assuming one fixed schema/height for the whole chain's lifetime.

### Proof of Concept
Conceptual PoC:
1. Deploy/track the Ethereum sync-committee light client starting from a trusted checkpoint prior to the Electra fork (field count fits in `EXECUTION_PAYLOAD_INDEX_LOG2 = 5`/32-leaf tree for `BeaconState`).
2. After Electra activates on mainnet, `BeaconState` gains ~9 new top-level fields, requiring `EXECUTION_PAYLOAD_INDEX_LOG2 = 6`/64-leaf tree and different generalized indices (as already reflected in the repo's post-Electra constants, e.g. `EXECUTION_PAYLOAD_INDEX = 88`, log2 `6`, in [5](#0-4) ).
3. Submit a legitimate post-Electra `VerifierStateUpdate` (or a pre-Electra one, if the network config is pinned to post-Electra values) to `verify_sync_committee_attestation`; because the `Config` for the network only supplies one fixed index/depth pair, the proof — despite being correctly generated for the *actual* on-chain schema at that slot — is checked against a Merkle tree height that does not match, causing `is_valid_merkle_branch` to fail for a valid state, or (in the reverse direction, a shallower fixed depth against a proof engineered by an attacker with extra padding) to spuriously validate a crafted branch, per [6](#0-5) .

### Citations

**File:** modules/consensus/sync-committee/verifier/src/lib.rs (L163-218)
```rust
	let is_merkle_branch_valid = is_valid_merkle_branch(
		&finalized_checkpoint
			.hash_tree_root()
			.map_err(|_| Error::MerkleizationError("Failed to hash finality checkpoint".into()))?,
		update.finality_proof.finality_branch.iter(),
		C::FINALIZED_ROOT_INDEX_LOG2 as usize,
		C::FINALIZED_ROOT_INDEX as usize,
		&update.attested_header.state_root,
	);

	if !is_merkle_branch_valid {
		Err(Error::InvalidMerkleBranch("Finality branch".into()))?;
	}

	// verify the associated execution header of the finalized beacon header.
	let mut execution_payload = update.execution_payload;
	let execution_payload_indices = [
		GeneralizedIndex(C::EXECUTION_PAYLOAD_STATE_ROOT_INDEX as usize),
		GeneralizedIndex(C::EXECUTION_PAYLOAD_BLOCK_NUMBER_INDEX as usize),
		GeneralizedIndex(C::EXECUTION_PAYLOAD_TIMESTAMP_INDEX as usize),
	];
	// `calculate_multi_merkle_root` panics on a short `multi_proof` because its final
	// `objects.get(&GeneralizedIndex(1)).unwrap()` cannot reconstruct the root. Reject
	// proofs whose helper-node count does not match what the algorithm requires so an
	// attacker-controlled `multi_proof` cannot panic the runtime via the public unsigned
	// consensus update path.
	if execution_payload.multi_proof.len() != get_helper_indices(&execution_payload_indices).len()
	{
		Err(Error::InvalidMerkleBranch("Execution payload multiproof length".into()))?;
	}
	let execution_payload_root = calculate_multi_merkle_root(
		&[
			Node::from_bytes(execution_payload.state_root.as_ref().try_into().expect("Infallible")),
			execution_payload.block_number.hash_tree_root().map_err(|_| {
				Error::MerkleizationError("Failed to hash execution payload".into())
			})?,
			execution_payload
				.timestamp
				.hash_tree_root()
				.map_err(|_| Error::MerkleizationError("Failed to hash timestamp".into()))?,
		],
		&execution_payload.multi_proof,
		&execution_payload_indices,
	);

	let is_merkle_branch_valid = is_valid_merkle_branch(
		&execution_payload_root,
		execution_payload.execution_payload_branch.iter(),
		C::EXECUTION_PAYLOAD_INDEX_LOG2 as usize,
		C::EXECUTION_PAYLOAD_INDEX as usize,
		&update.finalized_header.state_root,
	);

	if !is_merkle_branch_valid {
		Err(Error::InvalidMerkleBranch("Execution payload branch".into()))?;
	}
```

**File:** modules/consensus/sync-committee/primitives/src/constants.rs (L61-115)
```rust
pub const DOMAIN_SYNC_COMMITTEE: DomainType = DomainType::SyncCommittee;

pub const FINALIZED_ROOT_INDEX: u64 = 52;
pub const EXECUTION_PAYLOAD_INDEX: u64 = 56;
pub const NEXT_SYNC_COMMITTEE_INDEX: u64 = 55;

pub const FINALIZED_ROOT_INDEX_LOG2: u64 = 5;
pub const EXECUTION_PAYLOAD_INDEX_LOG2: u64 = 5;
pub const NEXT_SYNC_COMMITTEE_INDEX_LOG2: u64 = 5;

pub const ETH1_DATA_VOTES_BOUND_ETH: usize = (EPOCHS_PER_ETH1_VOTING_PERIOD * 32) as usize;
pub const ETH1_DATA_VOTES_BOUND_GNO: usize = (EPOCHS_PER_ETH1_VOTING_PERIOD * 16) as usize;

pub const BEACON_CONSENSUS_ID: [u8; 4] = *b"BEAC";
pub const GNOSIS_CONSENSUS_ID: [u8; 4] = *b"GNOS";

pub const MAX_DEPOSIT_REQUESTS_PER_PAYLOAD: usize = 2usize.saturating_pow(13);
pub const MAX_WITHDRAWAL_REQUESTS_PER_PAYLOAD: usize = 2usize.saturating_pow(16);
pub const MAX_CONSOLIDATION_REQUESTS_PER_PAYLOAD: usize = 2usize.saturating_pow(3);

pub const PENDING_DEPOSITS_LIMIT: usize = 2usize.saturating_pow(27);
pub const PENDING_PARTIAL_WITHDRAWALS_LIMIT: usize = 2usize.saturating_pow(27);
pub const PENDING_CONSOLIDATIONS_LIMIT: usize = 2usize.saturating_pow(18);

pub const PROPOSER_LOOK_AHEAD_LIMIT_ETHEREUM: usize = 64;
pub const PROPOSER_LOOK_AHEAD_LIMIT_GNO: usize = 32;

pub trait Config {
	const SLOTS_PER_EPOCH: Slot;
	const GENESIS_VALIDATORS_ROOT: [u8; 32];
	const BELLATRIX_FORK_VERSION: Version;
	const ALTAIR_FORK_VERSION: Version;
	const GENESIS_FORK_VERSION: Version;
	const ALTAIR_FORK_EPOCH: Epoch;
	const BELLATRIX_FORK_EPOCH: Epoch;
	const CAPELLA_FORK_EPOCH: Epoch;
	const CAPELLA_FORK_VERSION: Version;
	const DENEB_FORK_EPOCH: Epoch;
	const DENEB_FORK_VERSION: Version;
	const EPOCHS_PER_SYNC_COMMITTEE_PERIOD: Epoch;
	const EXECUTION_PAYLOAD_STATE_ROOT_INDEX: u64;
	const EXECUTION_PAYLOAD_BLOCK_NUMBER_INDEX: u64;
	const EXECUTION_PAYLOAD_TIMESTAMP_INDEX: u64;
	const EXECUTION_PAYLOAD_INDEX: u64;
	const NEXT_SYNC_COMMITTEE_INDEX: u64;
	const FINALIZED_ROOT_INDEX: u64;
	const FINALIZED_ROOT_INDEX_LOG2: u64;
	const EXECUTION_PAYLOAD_INDEX_LOG2: u64;
	const NEXT_SYNC_COMMITTEE_INDEX_LOG2: u64;
	const ELECTRA_FORK_VERSION: Version;
	const ELECTRA_FORK_EPOCH: Epoch;
	const FULU_FORK_VERSION: Version;
	const FULU_FORK_EPOCH: Epoch;
	const ID: [u8; 4];
}
```

**File:** modules/consensus/sync-committee/primitives/src/constants.rs (L163-191)
```rust
	impl Config for Mainnet {
		const SLOTS_PER_EPOCH: Slot = 32;
		const GENESIS_VALIDATORS_ROOT: [u8; 32] =
			hex_literal::hex!("4b363db94e286120d76eb905340fdd4e54bfe9f06bf33ff6cf5ad27f511bfe95");
		const BELLATRIX_FORK_VERSION: Version = hex_literal::hex!("02000000");
		const ALTAIR_FORK_VERSION: Version = hex_literal::hex!("01000000");
		const GENESIS_FORK_VERSION: Version = hex_literal::hex!("00000000");
		const ALTAIR_FORK_EPOCH: Epoch = 74240;
		const BELLATRIX_FORK_EPOCH: Epoch = 144896;
		const CAPELLA_FORK_EPOCH: Epoch = 194048;
		const CAPELLA_FORK_VERSION: Version = hex_literal::hex!("03000000");
		const DENEB_FORK_EPOCH: Epoch = 269568;
		const DENEB_FORK_VERSION: Version = hex_literal::hex!("04000000");
		const EPOCHS_PER_SYNC_COMMITTEE_PERIOD: Epoch = 256;
		const EXECUTION_PAYLOAD_STATE_ROOT_INDEX: u64 = 34;
		const EXECUTION_PAYLOAD_BLOCK_NUMBER_INDEX: u64 = 38;
		const EXECUTION_PAYLOAD_TIMESTAMP_INDEX: u64 = 41;
		const EXECUTION_PAYLOAD_INDEX: u64 = 88;
		const NEXT_SYNC_COMMITTEE_INDEX: u64 = 87;
		const FINALIZED_ROOT_INDEX: u64 = 84;
		const FINALIZED_ROOT_INDEX_LOG2: u64 = 6;
		const EXECUTION_PAYLOAD_INDEX_LOG2: u64 = 6;
		const NEXT_SYNC_COMMITTEE_INDEX_LOG2: u64 = 6;
		const ELECTRA_FORK_VERSION: Version = hex_literal::hex!("05000000");
		const ELECTRA_FORK_EPOCH: Epoch = 364032;
		const FULU_FORK_EPOCH: Epoch = 411392;
		const FULU_FORK_VERSION: Version = hex_literal::hex!("06000000");
		const ID: [u8; 4] = BEACON_CONSENSUS_ID;
	}
```

**File:** docs/content/protocol/cryptography/merkle-trees/binary.mdx (L76-80)
```text
## Second Pre-image Attacks

[Second pre-image attacks](https://en.wikipedia.org/wiki/Merkle_tree#Second_preimage_attack) arise when merkle tree proof schemes do not check the tree depth when verifying merkle proofs. This allows for attackers to construct either arbitrarily deep or shallow trees that have the same root hash as the verifier’s, in order to fool the verifier that some forged items are in the original tree.

In order to mitigate this, given our current proof scheme, **it is necessary that the verifier knows the number of items in the tree**. The height of the tree can be computed from it's leaf count and compared to the length of the 2D proof array (which encodes the height of the tree). If they do not match then the proof can safely be rejected because it describes a different tree and is  attempting to perform a pre-image collision attack.
```
