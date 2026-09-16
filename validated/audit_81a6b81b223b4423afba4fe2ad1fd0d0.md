### Title
Unchecked-length `copy_from_slice` into fixed `[u8;65]` BEEFY signature buffer panics the node on a permissionless proof submission - ([File: evm/rust/src/conversions.rs])

### Summary
`impl From<Vote> for SignatureWithAuthorityIndex` in `evm/rust/src/conversions.rs` copies an attacker-supplied, variable-length Solidity `bytes` field into a fixed-size `[u8; 65]` array with `copy_from_slice` and no length check, mirroring the RIOT `strcpy`/`gcoap` bug class (checked-the-wrong-thing / didn't-check-at-all before a fixed-size copy). This conversion sits on the `pallet-beefy-consensus-proofs::submit_proof` (`PROOF_TYPE_NAIVE`) path, which decodes a relayer-submitted ABI proof (`BeefyConsensusProof` → `RelayChainProof.signedCommitment.votes: Vote[]`) with `signature: bytes` — a field whose length is fully attacker-controlled at the ABI layer.

### Finding Description [1](#0-0) 

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

`Vote.signature` is Solidity `bytes` (variable length, ABI-decoded from proof bytes submitted by any caller of `submit_proof`) — not a fixed `bytes65`. `TSignature = [u8; 65]` [2](#0-1)  requires an exact-length source slice; `copy_from_slice` panics ("source slice length does not match destination") if `sig_bytes.len() != 65`.

This is exactly the RIOT bug class: `gcoap_dns_server_proxy_get()` checked the wrong variable's length before `strcpy`, and `_gcoap_forward_proxy_copy_options()` performed no explicit size check before copying into a fixed `COAP_ETAG_LENGTH_MAX` buffer. Here there is *no* length check at all before the fixed-size copy — the omission is even more direct.

The rest of the codebase shows this exact hardening pattern was applied everywhere else a fixed buffer receives untrusted bytes (e.g. `modules/utils/crypto/src/verification.rs:42-47` checks `signature.len() != 65` before copying; `tesseract/consensus/beefy/src/prover.rs:69-78` checks length before `copy_from_slice`; `modules/utils/serde/src/lib.rs` and `modules/ismp/core/src/host.rs:470-489` document and test regressions for exactly this pattern), which confirms this is a known, actively-guarded bug class in this codebase — but the `Vote → SignatureWithAuthorityIndex` conversion was missed.

### Impact Explanation
Panicking Rust code compiled into the Substrate runtime (`#[cfg(feature = "substrate")]`) traps the wasm executor. A transaction that reaches `Decode`-then-convert with a malformed vote signature causes the extrinsic's execution to trap rather than cleanly error, which in a Substrate runtime context is a controlled/uncontrolled panic depending on where it is invoked (inside `on_initialize`/dispatch it can fail the block; inside dispatch-time weight-metered execution it typically aborts the transaction, but if reached from an unsigned/free path or from block-building it can DoS the collator). At minimum this is a denial-of-service on the BEEFY consensus-update path, which every other cross-chain message and state proof on Hyperbridge depends on (a poisoned/crashed consensus update path is "a route unable to deliver messages"). It is also invoked from off-chain relayer/tesseract binaries processing proofs, where a panic can crash the relaying process.

### Likelihood Explanation
`submit_proof` on `pallet-beefy-consensus-proofs` is called with a proof blob; for `PROOF_TYPE_NAIVE` this is ABI-decoded into `BeefyConsensusProof`, and the nested `votes: Vote[]` array's `signature` field is unconstrained `bytes` at the ABI level — any relayer/submitter can encode a `Vote` with `signature` of length ≠ 65 (e.g., 0 or 64 bytes) and pass all earlier structural checks (only `MaxProofSize` bounded-vec and `abi_decode_params` succeed/fail on encoding well-formedness, not per-field length of a `bytes` blob). This is a single, low-cost, permissionless extrinsic submission — very likely exploitable if this exact code path executes the conversion before any BEEFY signature verification would reject an all-zero/garbage signature (verification happens on the decoded `TSignature`, which is only reached *after* this fixed-size copy already panics).

### Recommendation
Add an explicit length check before the fixed-size copy in `evm/rust/src/conversions.rs`:
```rust
impl TryFrom<Vote> for SignatureWithAuthorityIndex {
    type Error = ...;
    fn try_from(value: Vote) -> Result<Self, Self::Error> {
        let sig_bytes = value.signature.to_vec();
        let signature: TSignature = sig_bytes
            .as_slice()
            .try_into()
            .map_err(|_| /* InvalidSignatureLength */)?;
        Ok(SignatureWithAuthorityIndex {
            signature,
            index: value.authorityIndex.try_into().map_err(...)?,
        })
    }
}
```
and propagate the error through `From<RelayChainProof> for MmrProof` (which currently calls `.into()` unconditionally on each vote) so a malformed proof is rejected with a decode error instead of panicking, consistent with the `verify_sr25519`/`verification.rs` pattern already used elsewhere in the codebase.

### Proof of Concept
1. Craft a `BeefyConsensusProof` ABI payload where `relay.signedCommitment.votes[0].signature` is set to a `bytes` value of length 64 (or 0), with `authorityIndex` set to any in-range value.
2. Prefix with `PROOF_TYPE_NAIVE` and submit via `pallet_beefy_consensus_proofs::submit_proof` (any signed account, subject only to `MaxProofSize` bound-vec size — no per-field length validation occurs before this point) — see the encode/size checks exercised in [3](#0-2)  for the existing structural-validation boundary that this bypasses.
3. Dispatch proceeds through `ConsensusMessage::from(BeefyConsensusProof)` → `RelayChainProof::into::<MmrProof>()` → `Vote::into::<SignatureWithAuthorityIndex>()`, which executes `signature.copy_from_slice(&sig_bytes)` with `sig_bytes.len() != 65`, triggering a Rust panic/wasm trap during proof processing instead of a graceful `Err`.

### Citations

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

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L355-387)
```rust
	// 6. submit_proof oversized payload — `proof: BoundedVec<u8, MaxProofSize>` rejects at the
	//    txpool decode stage, before dispatch. We send `MaxProofSize + 1` bytes prefixed with
	//    `PROOF_TYPE_NAIVE`.
	let mut oversized_proof = vec![PROOF_TYPE_NAIVE; MAX_PROOF_SIZE + 1];
	oversized_proof[0] = PROOF_TYPE_NAIVE;
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&oversized_proof)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "oversized submit_proof must be rejected by the BoundedVec decode",);

	// 7. submit_proof with an unknown proof-type byte.
	let unknown_proof = vec![UNKNOWN_PROOF_TYPE; 64];
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&unknown_proof)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "unknown proof-type submit_proof must fail (UnknownProofType)",);

	// 8. submit_proof with malformed naive bytes. The byte 0 marks `PROOF_TYPE_NAIVE`, the rest is
	//    junk that won't ABI-decode as `BeefyConsensusProof`. Expect `AbiDecodeFailed`.
	let mut malformed_naive = vec![0u8; 128];
	malformed_naive[0] = PROOF_TYPE_NAIVE;
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&malformed_naive)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
```
