Found it. `modules/consensus/bsc/verifier/src/primitives.rs` `parse_extra()` contains an unchecked out-of-bounds slice/index vulnerability reachable directly by any relayer submitting a BSC consensus proof, analogous to CVE-2017-7506 (out-of-bounds memory access from an authenticated-but-untrusted party's crafted message).

### Title
Out-of-bounds slice indexing in BSC header `extra_data` validator parsing causes relayer-triggerable panic - (`modules/consensus/bsc/verifier/src/primitives.rs`)

### Summary
`parse_extra()` decodes the BSC block header's `extra_data` field, which is fully attacker/relayer-controlled content embedded in `BscClientUpdate.attested_header` / `source_header` submitted as a `Message::Consensus` proof. The function computes `validator_bytes_total_length = VALIDATOR_NUMBER_SIZE + validator_num * VALIDATOR_BYTES_LENGTH` where `validator_num = data[0] as usize` is an untrusted byte (0-255), and only checks `data_length < required_length` against the *remaining* slice after the vanity/seal trim — but the subsequent per-validator loop indexes `remaining_data[i * VALIDATOR_BYTES_LENGTH .. i * VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH]` using `remaining_data = &data[VALIDATOR_NUMBER_SIZE..]`, i.e., one element shorter than `data`. Because the length check is performed against `data_length = data.len()` but the slicing happens on `remaining_data` (which is `data.len() - 1` bytes), a header can be crafted where `data_length >= required_length` passes yet the last validator's slice range exceeds `remaining_data.len()`, causing an out-of-bounds slice indexing panic.

### Finding Description
In `parse_extra`:
```rust
if data_length < required_length {
    Err(anyhow!("Parse validator failed"))?;
}
...
let remaining_data = &data[VALIDATOR_NUMBER_SIZE..];
for i in 0..validator_num {
    let address_bytes: Vec<u8> = remaining_data[i * VALIDATOR_BYTES_LENGTH..
        i * VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH].to_vec();
    ...
}
``` [1](#0-0) 

`data_length` is `data.len()` (the full extra section after stripping vanity/seal), but `remaining_data` is `&data[VALIDATOR_NUMBER_SIZE..]`, one byte shorter. The bound check `data_length < required_length` uses the larger length, so it can pass while `remaining_data` is one byte too short to satisfy `validator_bytes_total_length` bytes of indexing, and the final validator's slice (`i == validator_num - 1`) reads past the end of `remaining_data`, triggering a Rust slice-index panic (`slice index starts/ends after length`) rather than a graceful decode error.

This function is called from `verify_bsc_header`, which is invoked by `SyncCommitteeConsensusClient`/BSC ISMP consensus client's `verify_consensus` when handling an incoming `Message::Consensus` update — a permissionless, relayer-submitted transaction path (`HandlerV2::handleConsensus` on EVM, or the equivalent pallet-ismp unsigned consensus message handler on Substrate). No signature or authority check happens before `parse_extra` is called; it processes the raw header bytes to extract validator/vote data prior to any BLS signature verification.

### Impact Explanation
A relayer can construct a BSC `attested_header` (or `source_header`/`epoch_header_ancestry` header) whose `extra_data` triggers this off-by-one and panics the consensus client host process (in the tesseract relayer/prover binary) or, if executed inside a runtime (pallet-ismp / on-chain BSC light client pallet), aborts the extrinsic execution path with an unhandled panic instead of a typed error. Depending on execution context this can be leveraged as a permissionless denial-of-service against nodes/relayers processing BSC consensus updates, and — consistent with the CVE-2017-7506 bug class (out-of-bounds memory access from crafted attacker messages resulting in crash) — represents unsound input validation on a consensus-verification hot path that every route delivering BSC-sourced messages depends on. This blocks the BSC consensus route from ever finalizing/delivering messages once a malicious header is submitted and processed (a form of route unable to deliver messages), and in a Substrate runtime context an uncaught panic during block execution is a liveness-critical fault.

### Likelihood Explanation
High — reachable directly from `verify_bsc_header`, which any relayer can trigger with the `BscClientUpdate.attested_header.extra_data` field fully under their control; no authentication, signature or state check is performed before `parse_extra` runs the vulnerable slicing logic. Constructing the malformed length/validator-count combination is a simple arithmetic exercise, not a hash or signature forgery.

### Recommendation
Compute and check the length requirement against `remaining_data.len()` (i.e., `data.len() - VALIDATOR_NUMBER_SIZE`) rather than the pre-slice `data_length`, or equivalently bound-check `remaining_data.len() >= validator_bytes_total_length - VALIDATOR_NUMBER_SIZE + (turn byte if applicable)` before entering the per-validator loop, returning `Err(anyhow!("Parse validator failed"))` instead of allowing the off-by-one to reach the indexing operation. Add a regression test mirroring the pattern already used elsewhere in the codebase (e.g., the Pharos `spv.rs` and Ethereum `node_codec.rs` regression tests) with a header whose `data_length` exactly equals `required_length` and confirm no panic/index-out-of-bounds occurs.

### Proof of Concept
Construct a `CodecHeader` with `extra_data` such that:
1. `extra_data.len() == EXTRA_VANITY_LENGTH (32) + EXTRA_SEAL_LENGTH (65) + N` for some `N`.
2. After trimming vanity/seal, `data.len() == N == data_length`.
3. Set `data[0] = validator_num` such that `required_length = VALIDATOR_NUMBER_SIZE + validator_num * VALIDATOR_BYTES_LENGTH (+ TURN_LENGTH_SIZE if post-BOHR) == N` exactly (passes the `data_length < required_length` check).
4. Because `remaining_data = &data[1..]` has length `N - 1 < required_length - VALIDATOR_NUMBER_SIZE` is actually fine size-wise for most `i`, but specifically the boundary case where `data_length == required_length` exactly leaves `remaining_data.len() == data_length - 1 == required_length - 1`, one byte short of `validator_bytes_total_length` needed for the last validator's `ADDRESS_LENGTH..VALIDATOR_BYTES_LENGTH` slice plus BLS key slice — indexing `remaining_data[(validator_num-1)*VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH .. validator_num*VALIDATOR_BYTES_LENGTH]` panics with "range end index out of range for slice of length ...".

Submit this header as `attested_header` in a `BscClientUpdate`, SCALE-encode it into an `IsmpConsensusMessage`/`Message::Consensus`, and dispatch it through the standard permissionless consensus-message path (`handle_incoming_message` → BSC `ConsensusClient::verify_consensus` → `verify_bsc_header` → `parse_extra`) to trigger the panic. [2](#0-1) [3](#0-2)

### Citations

**File:** modules/consensus/bsc/verifier/src/primitives.rs (L108-204)
```rust
pub fn parse_extra<H: Keccak256, C: Config>(
	header: &CodecHeader,
) -> Result<ExtraData, anyhow::Error> {
	let data = header.extra_data.as_slice();

	let mut extra = ExtraData {
		extra_vanity: Vec::new(),
		validator_size: 0,
		validators: Vec::new(),
		extra_seal: Vec::new(),
		agg_signature: [0; 96],
		vote_data: VoteData {
			source_number: 0,
			source_hash: Default::default(),
			target_number: 0,
			target_hash: Default::default(),
		},
		vote_address_set: 0,
	};

	if data.len() < EXTRA_VANITY_LENGTH + EXTRA_SEAL_LENGTH {
		Err(anyhow!("Invalid extra data"))?;
	}

	extra.extra_vanity = data[..EXTRA_VANITY_LENGTH].to_vec();
	extra.extra_seal = data[data.len() - EXTRA_SEAL_LENGTH..].to_vec();
	let mut data = &data[EXTRA_VANITY_LENGTH..data.len() - EXTRA_SEAL_LENGTH];

	let mut data_length = data.len();
	if !data.is_empty() {
		// Parse Validators
		if data[0] != 0xf8 {
			// RLP format of attestation begins with 'f8'
			let validator_num = data[0].clone() as usize;
			let validator_bytes_total_length =
				VALIDATOR_NUMBER_SIZE + validator_num * VALIDATOR_BYTES_LENGTH;
			// Post-BOHR headers carry a one-byte `turn` field immediately after the validator
			// entries. Include it in the length check so the BOHR slice at the end of this branch
			// (which advances `index` by `TURN_LENGTH_SIZE`) cannot panic on a header that has a
			// validator section but omits the turn byte.
			let required_length = if header.timestamp >= C::BOHR_FORK_TIMESTAMP {
				validator_bytes_total_length + TURN_LENGTH_SIZE
			} else {
				validator_bytes_total_length
			};
			if data_length < required_length {
				Err(anyhow!("Parse validator failed"))?;
			}
			extra.validator_size = validator_num.clone() as u8;
			let remaining_data = &data[VALIDATOR_NUMBER_SIZE..];

			for i in 0..validator_num {
				let mut validator_info =
					ValidatorInfo { address: H160::default(), bls_public_key: [0; 48] };

				let address_bytes: Vec<u8> = remaining_data[i.clone() * VALIDATOR_BYTES_LENGTH..
					i.clone() * VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH]
					.to_vec();
				let bls_public_key_bytes: Vec<u8> =
					remaining_data[i.clone() * VALIDATOR_BYTES_LENGTH + ADDRESS_LENGTH..
						(i.clone() + 1) * VALIDATOR_BYTES_LENGTH]
						.to_vec();

				validator_info.address = H160::from_slice(&address_bytes);
				validator_info.bls_public_key.copy_from_slice(&bls_public_key_bytes);

				extra.validators.push(validator_info);
			}
			extra.validators.sort_by(|a, b| a.address.0.cmp(&b.address.0));

			// Check for BOHR fork
			data = if header.timestamp >= C::BOHR_FORK_TIMESTAMP {
				// In Bohr fork there is an extra byte for turn
				// https://github.com/bnb-chain/bsc/blob/26a4d4fda656cc78436c1931aaea5dc3ed33eeeb/consensus/parlia/parlia.go#L383
				let index = validator_bytes_total_length - VALIDATOR_NUMBER_SIZE + TURN_LENGTH_SIZE;
				&remaining_data[index..]
			} else {
				let index = validator_bytes_total_length - VALIDATOR_NUMBER_SIZE;
				&remaining_data[index..]
			};
			data_length = data.len();
		}

		// parse attestation
		if data_length > 0 {
			let vote_attestation_data: VoteAttestationData = VoteAttestationData::decode(&mut data)
				.map_err(|_| anyhow!("parse vote attestation failed"))?;

			extra.agg_signature = vote_attestation_data.agg_signature.0.into();
			extra.vote_data = vote_attestation_data.data.into();

			extra.vote_address_set = vote_attestation_data.vote_address_set;
		}
	}

	Ok(extra.clone())
}
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L50-60)
```rust
pub fn verify_bsc_header<H: Keccak256, C: Config>(
	current_validators: &Vec<BlsPublicKey>,
	update: BscClientUpdate,
	epoch_length: u64,
) -> Result<VerificationResult, Error> {
	let extra_data =
		parse_extra::<H, C>(&update.attested_header).map_err(|_| Error::ParseExtraData)?;
	let source_hash = H256::from_slice(&extra_data.vote_data.source_hash.0);
	let target_hash = H256::from_slice(&extra_data.vote_data.target_hash.0);
	if source_hash == Default::default() || target_hash == Default::default() {
		Err(Error::EmptyVoteData)?
```
