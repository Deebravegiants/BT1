## Title
Panic-on-untrusted-length in BEEFY `Vote → SignatureWithAuthorityIndex` conversion causes a denial-of-service on the relay-submitted consensus proof path - ([File: evm/rust/src/conversions.rs])

### Summary
`evm/src/consensus/Types.sol` defines the BEEFY `Vote` struct with an attacker/relayer-controlled `bytes signature` field (no length constraint at the ABI level): [1](#0-0) 

The Rust-side conversion that turns this into the internal fixed-size signature type does not validate the length before copying: [2](#0-1) 

```rust
impl From<Vote> for SignatureWithAuthorityIndex {
	fn from(value: Vote) -> Self {
		let sig_bytes = value.signature.to_vec();
		let mut signature: TSignature = [0u8; 65];
		signature.copy_from_slice(&sig_bytes);
		...
	}
}
```

`TSignature` is `[u8; 65]` [3](#0-2) . `copy_from_slice` panics whenever the source slice length does not equal exactly 65 bytes.

### Finding Description
This is a direct analog of CVE-2019-11745's bug class: writing a variable/attacker-supplied byte buffer into a fixed-size block without first checking that the length matches. In NSS's C code this manifested as an out-of-bounds heap write; here Rust's memory safety converts the same missing-length-check into an unconditional `panic!`/process abort (`copy_from_slice` traps on any length mismatch rather than corrupting memory), but the root cause — decoding externally-supplied proof data into a fixed-size array without a length guard on the untrusted-input boundary — is identical.

This exact pattern was already identified and fixed elsewhere in the codebase for a very similar case (`consensus_state_id` deserialization, `[u8;4]`), where the code comments explicitly call out that "`copy_from_slice` traps on a length mismatch... reachable from untrusted input... so the length is now checked up-front": [4](#0-3) [5](#0-4) 

The `From<Vote> for SignatureWithAuthorityIndex` conversion at `evm/rust/src/conversions.rs:356-366` was not given the same treatment. It sits in the `RelayChainProof`/`MmrProof` conversion chain (`From<RelayChainProof> for MmrProof`, `From<MmrProof> for RelayChainProof`) that round-trips BEEFY consensus proof data between the on-chain ABI representation and the internal verifier representation: [6](#0-5) 

Every other site in the codebase that converts a raw signature byte-slice into `[u8; 65]` uses `try_into()`/`TryFrom` with an explicit error or `.expect()` with a documented length assumption from a *trusted, locally-fetched* RPC source (e.g. `modules/consensus/beefy/verifier/src/test.rs:158-160`, `modules/pallets/testsuite/src/tests/pallet_ismp_beefy.rs:115-117`) — not from data supplied by an arbitrary caller through the EVM host's proof-verification entrypoint.

### Impact Explanation
Because `EcdsaBeefy.verify` / `SP1Beefy.verify` on the EVM side accept caller-supplied `RelayChainProof`/`Vote[]` structures (decoded via `abi.decode`) as part of the public `IConsensusV2.verify(bytes,bytes)` interface [7](#0-6) , any code path on the Rust side that mirrors/consumes this ABI-decoded proof and calls `Into::<SignatureWithAuthorityIndex>::into(vote)` on a `Vote` whose `signature` field is not exactly 65 bytes will panic. In a relayer/light-client binary or off-chain SP1 prover/verifier component, this becomes a crash (denial of service) triggerable by any party who can submit a malformed consensus proof containing a non-65-byte signature, since the length is entirely attacker-controlled ABI-decoded `bytes`.

### Likelihood Explanation
High reachability by construction: `Vote.signature` is `bytes` with no length assertion in Solidity, and the conversion is invoked unconditionally on every element of the votes array whenever this Rust conversion path is exercised (e.g., relayer/tesseract components or test/verification tooling that round-trip ABI-decoded proofs through `beefy_verifier_primitives` types). No signature validity or supermajority check occurs before this conversion, so a caller only needs to submit any BEEFY-shaped proof with a wrong-length vote signature to trigger it.

### Recommendation
Replace the unchecked `copy_from_slice` with a length-checked conversion (e.g. `TryFrom`/`try_into` returning an error, mirroring the existing fixes for `consensus_state_id`/`as_utf8_string` and the `to_bytes_32` pattern used elsewhere): [8](#0-7) 
Reject `Vote`s whose `signature` length is not exactly 65 bytes with a proper error instead of panicking, and propagate that error through the `From<RelayChainProof> for MmrProof` chain (changing it to `TryFrom` if needed).

### Proof of Concept
1. Construct a `RelayChainProof` (or `MmrProof`/`SP1BeefyProof`) whose `signedCommitment.votes` array contains a `Vote` with `signature` set to a `bytes` value of length ≠ 65 (e.g., 64 or 66 bytes) — trivial via ABI encoding since Solidity places no length constraint on `bytes signature`.
2. Feed this proof through any Rust code path that performs `Into::<SignatureWithAuthorityIndex>::into(vote)` (i.e., `From<RelayChainProof> for MmrProof`, exercised by relayer/prover components consuming ABI-decoded proofs).
3. `signature.copy_from_slice(&sig_bytes)` at `evm/rust/src/conversions.rs:360` panics because `sig_bytes.len() != 65`, aborting the calling task/thread — a denial of service on that consensus-verification component.

*(Note: full reachability from an unprivileged end-to-end relayer submission into this specific Rust conversion could not be exhaustively traced within the available index — the code's presence, exact panic condition, and the established precedent of fixing the same bug pattern elsewhere in this codebase are confirmed by the citations above.)*

### Citations

**File:** evm/src/consensus/Types.sol (L141-146)
```text
struct Vote {
    // secp256k1 signature from a member of the authority set
    bytes signature;
    // 0-based index of the authority in the authority set
    uint256 authorityIndex;
}
```

**File:** evm/rust/src/conversions.rs (L356-366)
```rust
	impl From<Vote> for SignatureWithAuthorityIndex {
		fn from(value: Vote) -> Self {
			let sig_bytes = value.signature.to_vec();
			let mut signature: TSignature = [0u8; 65];
			signature.copy_from_slice(&sig_bytes);
			SignatureWithAuthorityIndex {
				signature,
				index: value.authorityIndex.try_into().expect("authority index out of bounds"),
			}
		}
	}
```

**File:** evm/rust/src/conversions.rs (L368-389)
```rust
	impl From<RelayChainProof> for MmrProof {
		fn from(value: RelayChainProof) -> Self {
			let leaf_index: u64 =
				value.latestMmrLeaf.leafIndex.try_into().expect("mmr leaf index out of bounds");
			let items: Vec<H256> = value.mmrProof.into_iter().map(|h| H256(h.0)).collect();
			let mmr_proof = LeafProof {
				leaf_indices: vec![leaf_index],
				leaf_count: leaf_index.saturating_add(1),
				items,
			};

			MmrProof {
				signed_commitment: BvpSignedCommitment {
					commitment: value.signedCommitment.commitment.into(),
					signatures: value.signedCommitment.votes.into_iter().map(Into::into).collect(),
				},
				latest_mmr_leaf: value.latestMmrLeaf.into(),
				mmr_proof,
				authority_proof: value.proof.into_iter().map(|h| h.0).collect(),
			}
		}
	}
```

**File:** modules/consensus/beefy/primitives/src/lib.rs (L45-46)
```rust
/// Authority Signature type
pub type TSignature = [u8; 65];
```

**File:** modules/utils/serde/src/lib.rs (L118-136)
```rust
	/// Deserialize a string into utf8 bytes
	///
	/// The string must be exactly 4 bytes long (bytes, not chars — a 4-char string of
	/// multi-byte codepoints is rejected). Anything else is a deserialization error; this
	/// runs on untrusted RPC input, so it must never panic.
	pub fn deserialize<'de, D, T>(deserializer: D) -> Result<T, D::Error>
	where
		D: serde::Deserializer<'de>,
		T: From<[u8; 4]>,
	{
		let s = <String>::deserialize(deserializer)?;

		// `s.len()` is the utf-8 byte length, which is what the `[u8; 4]` needs to match.
		let bytes: [u8; 4] = s
			.as_bytes()
			.try_into()
			.map_err(|_| serde::de::Error::invalid_length(s.len(), &"a 4-byte utf-8 string"))?;
		Ok(bytes.into())
	}
```

**File:** modules/ismp/core/src/host.rs (L470-474)
```rust
	// A malformed `SUBSTRATE-`/`TNDRMINT-` id whose byte length is not exactly 4
	// must return an error rather than panic. The id is copied into a `[u8; 4]`,
	// and `copy_from_slice` traps on a length mismatch — in the runtime this is a
	// wasm trap reachable from untrusted input (e.g. `BandwidthManager.purchase`),
	// so the length is now checked up-front (matching the `RELAY-` arm).
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L96-104)
```text
    function verify(bytes calldata previousState, bytes calldata proof)
        external
        pure
        returns (bytes memory, IntermediateState[] memory, uint256)
    {
        BeefyConsensusState memory consensusState = abi.decode(previousState, (BeefyConsensusState));
        (RelayChainProof memory relay, ParachainProof memory parachain) =
            abi.decode(proof, (RelayChainProof, ParachainProof));

```

**File:** modules/ismp/state-machines/evm/src/utils.rs (L118-128)
```rust
pub(super) fn to_bytes_32(bytes: &[u8]) -> Result<[u8; 32], Error> {
	if bytes.len() != 32 {
		return Err(EvmStateMachineError::BadByteLength(bytes.len()).into());
	}

	let mut array = [0u8; 32];

	array.copy_from_slice(&bytes);

	Ok(array)
}
```
