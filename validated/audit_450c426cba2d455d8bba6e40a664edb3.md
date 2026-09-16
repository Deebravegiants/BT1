Confirmed: `Vote.signature` in `evm/src/consensus/Types.sol:141-146` is a dynamic `bytes` field, entirely attacker-controlled (submitted on-chain by any relayer as part of a BEEFY `SignedCommitment`). The Rust-side `From<Vote> for SignatureWithAuthorityIndex` conversion in `evm/rust/src/conversions.rs:356-366` copies this untrusted byte slice into a fixed 65-byte array without checking its length first, unlike the prover's own construction path (`modules/consensus/beefy/prover/src/lib.rs:236-251`) which explicitly guards `if sig.len() != 65 { return None; }` before calling `copy_from_slice`. This asymmetry is the direct analog of CVE-2017-9115's `half.h` bug class: a fixed-size buffer write driven by an external, unvalidated length field, causing a crash (panic) rather than a controlled decode error.

### Title
Length-unchecked `copy_from_slice` into fixed 65-byte buffer from attacker-supplied `Vote.signature` panics the BEEFY consensus conversion path - (File: `evm/rust/src/conversions.rs`)

### Summary
The Solidity `Vote` struct (`evm/src/consensus/Types.sol:141-146`) carries an unconstrained `bytes signature` field that is populated by whoever submits a BEEFY `SignedCommitment`/`RelayChainProof` to the consensus client. The corresponding Rust conversion `impl From<Vote> for SignatureWithAuthorityIndex` (`evm/rust/src/conversions.rs:356-366`) does `sig_bytes.to_vec()` then `signature.copy_from_slice(&sig_bytes)` into a `[0u8; 65]` array without first verifying `sig_bytes.len() == 65`. `copy_from_slice` panics on any length mismatch.

### Finding Description [1](#0-0) 
constructs `TSignature` (`[u8; 65]`) from a `Vote.signature` that originates from [2](#0-1) 
an arbitrary-length `bytes` field with no on-chain length validation before this conversion executes. Contrast this with the trusted-generation path in the prover, which explicitly filters out any signature whose length isn't exactly 65 bytes before doing the same array copy: [3](#0-2) 
The conversion in `conversions.rs` has no equivalent guard — it is the "root cause" analog to the OpenEXR `half.h` bug: a size-2 (there, 65-byte here) write performed against a length that was never checked against the destination's fixed capacity, driven entirely by external, untrusted input.

### Impact Explanation
`copy_from_slice` panicking is a Rust panic, not a silent buffer overflow (Rust bounds-checks slice copies and aborts rather than corrupting memory), but the effect on availability is directly analogous to the CVE's "cause the application to crash" outcome. Any relayer or party able to submit a malformed BEEFY `SignedCommitment`/`Vote` with a `signature` field whose length is not 65 bytes can crash the process performing this conversion, denying consensus-proof processing and halting BEEFY-based message delivery/finality verification on the affected route until the process is restarted — a route-unable-to-deliver-messages condition.

### Likelihood Explanation
`Vote.signature` is a plain dynamic `bytes` array with no length assertion anywhere in the Solidity types or (as far as located) at the point of this Rust-side conversion. Any actor capable of constructing a `SignedCommitment`/`RelayChainProof`/vote list that reaches this conversion function can trigger it with a single malformed vote entry — this requires only crafting calldata, not privileged access.

### Recommendation
Add an explicit length check (`if sig_bytes.len() != 65 { return Err(...) / panic-free path }`) before `copy_from_slice` in the `From<Vote> for SignatureWithAuthorityIndex` implementation, mirroring the guard already present in `modules/consensus/beefy/prover/src/lib.rs:242`. Prefer `TryFrom` returning a `Result` over an infallible `From` so malformed input is rejected gracefully rather than panicking.

### Proof of Concept
1. Construct a BEEFY `SignedCommitment` (or `RelayChainProof`) containing a `Vote` whose `signature` field is any length other than 65 bytes (e.g., 0 or 64 bytes).
2. Submit it through the path that triggers the Rust-side `From<Vote> for SignatureWithAuthorityIndex` conversion in `evm/rust/src/conversions.rs`.
3. `signature.copy_from_slice(&sig_bytes)` panics because `sig_bytes.len() != 65`, aborting the process handling the conversion.

Note: I was not able to fully trace which production binary (client/host/relayer) directly invokes this `evm/rust/src/conversions.rs` conversion function at runtime versus only in tests, since the crate is behind a `substrate` feature flag and used across multiple consumer binaries; if the code index is missing files that would clarify this call path, a full Devin session with repository access would be needed to confirm the exact reachable entry point.

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

**File:** evm/src/consensus/Types.sol (L141-146)
```text
struct Vote {
    // secp256k1 signature from a member of the authority set
    bytes signature;
    // 0-based index of the authority in the authority set
    uint256 authorityIndex;
}
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
