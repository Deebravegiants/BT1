### Title
Unchecked-length `copy_from_slice` panics in the BEEFY consensus-proof Solidity→Rust conversion path - ([File: evm/rust/src/conversions.rs])

### Summary
`impl From<Vote> for SignatureWithAuthorityIndex` in `evm/abi`/`evm/rust`'s conversion layer copies an ABI-decoded, attacker/relayer-controlled `bytes` field straight into a fixed 65-byte array with `copy_from_slice` and no length check, mirroring the CVE-2023-6175 bug class (buffer copy without checking size of input) that causes Wireshark to crash on a crafted file.

### Finding Description
`From<Vote> for SignatureWithAuthorityIndex` takes `value.signature` — an `alloy_primitives::Bytes` field coming from the Solidity `Vote` struct (`evm/src/consensus/Types.sol`) that is populated purely by ABI-decoding the untrusted proof bytes a relayer submits — and does: [1](#0-0) 
```rust
impl From<Vote> for SignatureWithAuthorityIndex {
    fn from(value: Vote) -> Self {
        let sig_bytes = value.signature.to_vec();
        let mut signature: TSignature = [0u8; 65];
        signature.copy_from_slice(&sig_bytes);
        ...
```
There is no `if sig_bytes.len() != 65 { return Err(...) }` guard before the copy, unlike the analogous conversions elsewhere in the codebase that were explicitly hardened against this exact pattern (e.g. `modules/utils/crypto/src/verification.rs:42-47` checks `signature.len() != 65` before `copy_from_slice`, and `modules/utils/bls-utils/src/ssz/byte_vector.rs:48-56` was specifically patched with a length check and a regression-test comment explaining that an unchecked `copy_from_slice` on untrusted, attacker-supplied wire data previously crashed a production node's RPC worker thread). `Vote.signature` in Solidity is a dynamic `bytes` type with no length constraint enforced by the ABI decoder, so any length other than 65 (0, 64, 66, or arbitrary) reaches this line and triggers a Rust slice-length-mismatch panic (`copy_from_slice` panics when `src.len() != dst.len()`).

This conversion sits in the path that reconstructs Substrate/BEEFY consensus types (`SignatureWithAuthorityIndex`, `SignedCommitment`) from Solidity-ABI-decoded `BeefyConsensusProof`/`Vote` structures used by the "naive"/ECDSA BEEFY consensus-proof verification flow (`PROOF_TYPE_NAIVE`), which is exactly the kind of unprivileged, relayer-submitted consensus update `EvmHost`/`HandlerV2` dispatch relies on for cross-chain message delivery.

### Impact Explanation
A relayer or any party able to submit a BEEFY consensus proof can construct a `Vote` with a `signature` field of any length other than 65 bytes. When this reaches `From<Vote> for SignatureWithAuthorityIndex`, the process panics instead of returning a typed verification error. Depending on which side executes this conversion (on-chain WASM runtime execution vs. an off-chain relayer/verifier process), this manifests as either an unhandled runtime panic that aborts extrinsic execution unpredictably or a crash/DoS of the process performing consensus verification — a route unable to deliver messages, matching the "route unable to deliver messages" acceptance criterion for this bug class.

### Likelihood Explanation
High: this requires no special privilege — a single malformed consensus proof with a variable-length `signature` `bytes` field is sufficient, and ABI decoding places no length restriction on `bytes` fields, so a relayer or attacker fully controls this input.

### Recommendation
Add an explicit length check before the `copy_from_slice`, mirroring the fix already applied to the analogous `ByteVector<N>::decode` and `Signature::verify` sites in the same codebase:
```rust
impl TryFrom<Vote> for SignatureWithAuthorityIndex {
    type Error = ConversionError;
    fn try_from(value: Vote) -> Result<Self, Self::Error> {
        let sig_bytes = value.signature.to_vec();
        if sig_bytes.len() != 65 {
            return Err(ConversionError::InvalidSignatureLength(sig_bytes.len()));
        }
        let mut signature: TSignature = [0u8; 65];
        signature.copy_from_slice(&sig_bytes);
        Ok(SignatureWithAuthorityIndex { signature, index: value.authorityIndex.try_into()? })
    }
}
```
and propagate the resulting `Result` through all call sites instead of using an infallible `From`.

### Proof of Concept
1. Construct a Solidity `Vote { authorityIndex, signature }` where `signature` is any byte string whose length is not 65 (e.g. empty, or 64 bytes).
2. ABI-encode it as part of a `BeefyConsensusProof`/`SignedCommitment` and submit it through the naive BEEFY consensus-proof verification path that calls `Vote::into::<SignatureWithAuthorityIndex>()`.
3. `signature.copy_from_slice(&sig_bytes)` at [2](#0-1)  panics because `sig_bytes.len() != 65`, aborting the verification process instead of returning a decode/verification error.

### Citations

**File:** evm/rust/src/conversions.rs (L356-365)
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
```
