### Title
Unchecked `copy_from_slice` on ABI-decoded BEEFY `Vote.signature` panics the EVM-side proof conversion - ([File: evm/rust/src/conversions.rs])

### Summary
The `From<Vote> for SignatureWithAuthorityIndex` conversion in the EVM Rust bindings copies an attacker/relayer-controlled, variable-length `bytes` field directly into a fixed `[u8; 65]` buffer with `copy_from_slice`, without first checking that the length is exactly 65. This mirrors the CVE-2021-28660 bug class: writing/copying from an unchecked-length attacker input into a fixed-size buffer.

### Finding Description
`Vote` is the Solidity ABI struct (`evm/src/consensus/Types.sol`) whose `signature` field is declared as an unconstrained `bytes`: [1](#0-0) 

When this ABI-decoded proof is converted back into the internal verifier representation, the conversion is: [2](#0-1) 

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

`TSignature` is defined as `[u8; 65]`: [3](#0-2) 

`copy_from_slice` panics (Rust trap) whenever the source slice length does not exactly equal 65, rather than returning a `Result`. Because `Vote.signature` is an arbitrary-length `bytes` field in the ABI-decoded `RelayChainProof`/`SignedCommitment`/votes array, an attacker or malicious relayer submitting a BEEFY consensus proof can supply a signature of any length other than 65 (e.g. 0, 64, or 66 bytes) and trigger this panic during proof-to-internal-type conversion, before any cryptographic signature verification happens.

This is directly analogous to `rtw_wx_set_scan`'s unchecked write into the fixed `ssid[]` array from CVE-2021-28660: the destination is a fixed-size buffer, the source length is attacker-controlled, and no bounds/length check precedes the copy.

By contrast, the codebase has an established fix pattern elsewhere for the exact same shape of bug: BEEFY vote signature conversion at the prover/tesseract layer and in tests explicitly checks length before copying (`if sig.len() != 65 { return None; }` and `try_into().expect(...)` with `.filter_map`), and other decode boundaries in this codebase (e.g. `ByteVector<N>::decode`, `as_utf8_string::deserialize`, `consensus_state_id_from_str`) were hardened specifically because unchecked `copy_from_slice`/fixed-array conversions from untrusted input previously caused production panics (see the regression tests and comments referencing exactly this failure mode): [4](#0-3) [5](#0-4) 

The `From<Vote>` impl in `evm/rust/src/conversions.rs`, however, still uses the unchecked pattern.

### Impact Explanation
Where this conversion runs in a process that ingests untrusted, attacker-supplied `Vote.signature` bytes (e.g., any Rust component that ABI-decodes a submitted `RelayChainProof`/BEEFY consensus proof — such as an SP1/ZK guest program, relayer client, or verifier front-end using the `evm/rust` crate's `MmrProof: From<RelayChainProof>` conversion path), a malformed signature length causes an unrecoverable Rust panic/trap. In a `no_std`/wasm or SP1 zkVM guest context this aborts the whole execution; in a native process (relayer/prover binary) this crashes the worker thread/task, matching the exact "wasm trap reachable from untrusted input" and "crashed the production node's rpc worker thread" failure modes the codebase's own regression tests document for this bug class elsewhere. This is a denial-of-service on message/consensus-proof processing reachable from a single relayed proof, i.e., a route becoming unable to deliver/verify messages while the crash is being triggered repeatedly.

### Likelihood Explanation
High for any submitter capable of crafting a BEEFY `RelayChainProof`/`Vote` structure with a non-65-byte `signature` (trivial to construct, since Solidity `bytes` places no length constraint). The only uncertainty is which binary path actually calls this specific `From<Vote>` conversion on externally-supplied data at runtime (versus only being used to reconstruct proofs that were already generated trusted-side) — I was not able to fully trace a call site invoking `RelayChainProof -> MmrProof` (the direction that uses `From<Vote>`) from unmodified attacker input during my search; the confirmed call sites I found (`tesseract/consensus/beefy/zk/src/lib.rs`) go in the *opposite* direction (`SignatureWithAuthorityIndex -> Vote`, prover-generated, trusted). Because I could not conclusively confirm an untrusted-input call site for the `From<Vote>` direction within the available search budget, I flag this as the main residual uncertainty.

### Recommendation
Replace the unchecked `copy_from_slice` with a length-checked conversion, mirroring the pattern already used in `modules/consensus/beefy/prover/src/lib.rs`:
```rust
impl TryFrom<Vote> for SignatureWithAuthorityIndex {
    type Error = ...;
    fn try_from(value: Vote) -> Result<Self, Self::Error> {
        let sig_bytes = value.signature.to_vec();
        let signature: TSignature = sig_bytes
            .as_slice()
            .try_into()
            .map_err(|_| Error::InvalidSignatureLength(sig_bytes.len()))?;
        Ok(SignatureWithAuthorityIndex {
            signature,
            index: value.authorityIndex.try_into().map_err(|_| Error::AuthorityIndexOutOfBounds)?,
        })
    }
}
```
and update all call sites to propagate the error instead of panicking.

### Proof of Concept
1. Construct a `RelayChainProof` (ABI-encoded) whose `signedCommitment.votes[i].signature` is set to a `bytes` value of length ≠ 65 (e.g., 64 or 0 bytes) — trivially valid Solidity ABI encoding.
2. Feed this proof into any Rust code path that performs `MmrProof::from(relay_chain_proof)` / `SignatureWithAuthorityIndex::from(vote)` (the reverse conversion in `evm/rust/src/conversions.rs`).
3. `signature.copy_from_slice(&sig_bytes)` panics because `sig_bytes.len() != 65`, aborting the calling process/thread — a crash triggerable with a single malformed submitted proof and no valid signature required.

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

**File:** modules/consensus/beefy/primitives/src/lib.rs (L45-46)
```rust
/// Authority Signature type
pub type TSignature = [u8; 65];
```

**File:** modules/consensus/beefy/prover/src/lib.rs (L240-249)
```rust
			.filter_map(|(index, x)| {
				let sig = x.as_ref()?;
				if sig.len() != 65 {
					return None;
				}
				let mut temp = [0u8; 65];
				temp.copy_from_slice(&*sig.encode());
				let last = temp.last_mut().unwrap();
				*last = *last + 27;
				Some(SignatureWithAuthorityIndex { index: index as u32, signature: temp })
```

**File:** modules/utils/serde/src/lib.rs (L529-554)
```rust
	// `as_utf8_string` deserializes into a fixed `[u8; 4]`. It used to `copy_from_slice`
	// straight from the input, which panics on any length mismatch — and it runs on
	// untrusted RPC input (`consensus_state_id`), so the panic aborted the node's `rpc`
	// worker thread and took the process down. Wrong lengths must be serde errors.
	#[test]
	fn as_utf8_string_rejects_non_four_byte_input() {
		#[derive(Deserialize, Debug, PartialEq, Eq)]
		struct TestData {
			#[serde(with = "as_utf8_string")]
			id: [u8; 4],
		}

		for s in [
			"",          // 0 bytes
			"AB",        // 2 bytes
			"ABC",       // 3 bytes
			"ABCDE",     // 5 bytes
			"CERE0",     // 5 bytes — the value that crashed the production node
			"ABC\u{e9}", // 4 chars, 5 bytes: length is counted in bytes, not chars
		] {
			let json = serde_json::json!({ "id": s }).to_string();
			assert!(
				serde_json::from_str::<TestData>(&json).is_err(),
				"expected a deserialization error for {s:?}"
			);
		}
```
