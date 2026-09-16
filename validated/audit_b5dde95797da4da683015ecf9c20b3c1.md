Found it — this is a real analog of CVE-2021-28905 (reachable assertion, CWE-617): the `From<RelayChainProof> for MmrProof` conversion in `evm/rust/src/conversions.rs` panics via `.expect(...)` on attacker-controlled ABI-decoded fields, reachable on-chain through `pallet-beefy-consensus-proofs::submit_proof`, which is a normal signed extrinsic (no privileged origin, per `parachain/simtests/src/pallet_beefy_consensus_proofs.rs` submitting as `Keyring::Bob`).

### Title
Reachable panic via unchecked numeric truncation in EVM-proof-to-SCALE conversion for BEEFY consensus proofs - ([File: evm/rust/src/conversions.rs])

### Summary
`pallet_beefy_consensus_proofs::Pallet::verify_and_apply` (`modules/pallets/beefy-consensus-proofs/src/lib.rs:805`) accepts an unprivileged, signed `submit_proof` call whose payload is ABI-decoded into `SP1BeefyProof`/`BeefyConsensusProof` Solidity-mirrored types and then converted with `.into()` into the SCALE `Sp1BeefyProof`/`ConsensusMessage`/`MmrProof` types used by the verifier. Several of these `From` impls in `evm/rust/src/conversions.rs` use `.try_into().expect(...)` on values taken directly from attacker-controlled ABI fields (`U256` → `u64`/`u32`/`u8`), e.g. `leafIndex`, `blockNumber`, `validatorSetId`, `authorityIndex`, mmr-leaf `version`/`parentNumber`, authority-set `id`/`len`, `parachain leaf index`, and `leafCount`. Since these `U256` values come straight from relayer-supplied bytes, submitting a proof with any of these fields exceeding the target integer's range (e.g. `leafIndex > u64::MAX`, or `version > u8::MAX`) causes the `.expect()` to panic, which unwinds to a runtime panic/trap — the same class of bug as libyang's `lys_node_free()` reachable assertion: an attacker-controlled value bypasses proper validation and hits a hard-coded "cannot happen" invariant that in fact can happen from untrusted input.

### Finding Description
`verify_and_apply` in `modules/pallets/beefy-consensus-proofs/src/lib.rs:805-838` does:
```rust
let abi_proof = <ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof as SolType>::abi_decode_params(abi_payload)
    .map_err(|_| Error::<T>::AbiDecodeFailed)?;
let scale_proof: beefy_verifier_primitives::Sp1BeefyProof = abi_proof.into();
```
The `From<crate::sp1_beefy::SP1Beefy::SP1BeefyProof> for Sp1BeefyProof` impl (`evm/rust/src/conversions.rs:397-416`) does:
```rust
block_number: value.commitment.blockNumber.try_into().expect("block number out of bounds"),
validator_set_id: value.commitment.validatorSetId.try_into().expect("validator set id out of bounds"),
mmr_leaf: value.mmrLeaf.into(),   // -> PartialBeefyMmrLeaf conversion, also .expect()-laden
```
`PartialBeefyMmrLeaf` → `SpMmrLeaf` (line 249-274) does `value.version.try_into().expect("mmr leaf version out of bounds")` and `value.parentNumber.try_into().expect(...)` and authority-set `id`/`len` `.expect(...)`. The naive path (`BeefyConsensusProof`) similarly flows through `From<RelayChainProof> for MmrProof` (line 368-389), which does `value.latestMmrLeaf.leafIndex.try_into().expect("mmr leaf index out of bounds")`, and `From<Commitment> for SpCommitment` (line 334-354), which does `.first().expect("commitment has at least one payload entry")` on an attacker-supplied empty `payload` array.

None of these fields are range-checked before the `try_into()`/`expect()` calls, and the call site (`ValidateUnsigned`/dispatch of `submit_proof`) has no upstream bound on the numeric magnitude of ABI-decoded `U256` fields or the length of the `payload` array. A relayer or any signed account can call `submit_proof` with a crafted `abi_payload` (SP1 or NAIVE variant) carrying an out-of-range `U256` (e.g. `blockNumber = u64::MAX + 1`, `leafIndex` overflowing `u64`, or `version` overflowing `u8`) or an empty `payload` array, causing an `expect()` panic before any cryptographic verification takes place.

This directly parallels CVE-2021-28905: a value the code assumes is always well-formed (there `node->module` non-null; here bounded integer ranges / non-empty vectors) is in fact attacker-controlled and violates the assumption, triggering a reachable assertion/panic (CWE-617) instead of a graceful error.

### Impact Explanation
A panic inside pallet dispatch execution (via `#[frame_support::transactional]` in `verify_and_apply`) unwinds through the runtime's WASM execution. Depending on how the panic propagates through the FRAME executive/transactional wrapper, this can abort the current block's transaction processing, and — because `submit_proof` is callable by anyone with a signed account, permissionlessly and repeatedly — an attacker can deny availability of the BEEFY consensus update pipeline on the chain that hosts `pallet-beefy-consensus-proofs` (a coprocessor / nexus-style chain per the codebase's runtime wiring), stalling the flow of new consensus states, and therefore all downstream request/response delivery that depends on BEEFY consensus updates (a route unable to deliver messages). This is a protocol-wide availability impact reachable from a single submitted, unprivileged, signed transaction.

### Likelihood Explanation
High. `submit_proof` requires no special origin — any account with a nonce and inclusion fee can call it (confirmed by the simtest submitting as `Keyring::Bob`, a non-privileged test account). Crafting an ABI payload with an out-of-range `U256` field or empty `payload` array requires no cryptographic material and no knowledge of secrets; it is a pure malformed-input construction. The `AbiDecodeFailed` error path only catches ABI-decoding failures, not the subsequent `.into()` conversions, so the panicking code is unconditionally reached for any successfully ABI-decoded (but numerically out-of-range) payload.

### Recommendation
Replace every `.try_into().expect(...)` in `evm/rust/src/conversions.rs` (the `beefy` module, lines ~146-416) that converts attacker-controlled ABI (`U256`/array) fields into SCALE primitives (`u64`, `u32`, `u8`, non-empty `Vec`) with fallible conversions that propagate a typed error (e.g. `Error::AbiDecodeFailed` or a new `Error::AbiValueOutOfRange`) back through `From`/`TryFrom`, and update `verify_and_apply` in `modules/pallets/beefy-consensus-proofs/src/lib.rs` to use `TryFrom` instead of `Into` for these conversions so out-of-range values are rejected with a `DispatchError` rather than panicking. In particular fix: `commitment.blockNumber`/`validatorSetId`, `mmrLeaf.version`/`parentNumber`/`nextAuthoritySet.{id,len}`, `latestMmrLeaf.leafIndex`, `Vote.authorityIndex`, `Parachain.index`/`id`, `ParachainProof.leafCount`, and the empty-`payload` case in `From<Commitment> for SpCommitment`.

### Proof of Concept
1. Construct an ABI payload for the `PROOF_TYPE_SP1` (or `PROOF_TYPE_NAIVE`) variant of the beefy proof, valid enough to pass `abi_decode_params`, but set `commitment.blockNumber` (or `mmrLeaf.leafIndex`/`version`, or an empty `payload` array for the naive commitment) to a value outside the target Rust integer's range (e.g. `U256::MAX`, or `version = 300` for a `u8` target, or `payload = []`).
2. Submit as a normal signed extrinsic: `BeefyConsensusProofs::submit_proof(proof_bytes)` from any funded account (no admin/root needed).
3. Execution reaches `verify_and_apply` → `abi_proof.into()` → the vulnerable `.expect(...)` conversion → runtime panic, before any BLS/ECDSA/MMR verification is performed, aborting the extrinsic's execution path rather than returning `Error::<T>::AbiDecodeFailed`/`VerificationFailed`.