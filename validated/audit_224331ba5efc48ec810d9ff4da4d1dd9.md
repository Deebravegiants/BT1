Found the vulnerable analog. Two call sites in `verify_bsc_header` (`modules/consensus/bsc/verifier/src/lib.rs:172` and `:191`) convert validator BLS public-key bytes into a fixed-size `BlsPublicKey` (`[u8; 48]`) using `.as_slice().try_into().expect("Infallible")`. The `.expect("Infallible")` assumption is wrong: these bytes come from `parse_extra::<H, C>(...)`, which populates `ValidatorInfo::bls_public_key` from `remaining_data[...]` slices sized by `VALIDATOR_BYTES_LENGTH` in `modules/consensus/bsc/verifier/src/primitives.rs:163-172` — a length that is itself derived from the attacker-supplied `validator_num` byte and the raw `extra_data` of a submitted BSC header, not independently validated to equal 48 bytes at this specific call site. If that upstream invariant is ever violated (e.g. a header attested via `epoch_header_ancestry`, which is fully relayer-supplied), the `try_into()` fails and `.expect("Infallible")` panics — the exact class of bug the CVE describes (an unchecked length assumption feeding a fixed-size copy), except in Rust the "corruption" manifests as a reachable panic/trap during on-chain consensus-proof verification rather than memory corruption.

### Title
Unchecked length invariant on relayer-supplied BLS validator-key bytes can panic BSC consensus verification - (File: modules/consensus/bsc/verifier/src/lib.rs)

### Summary
`verify_bsc_header` derives `NextValidators` from `epoch_header_extra_data.validators`, converting each `val.bls_public_key` (a `Vec<u8>`) into the fixed-size `BlsPublicKey` (`[u8; 48]`) type via `.as_slice().try_into().expect("Infallible")` at [1](#0-0) and [2](#0-1) . This mirrors the CVE-2025-39849 pattern: an untrusted variable-length field is assumed to already satisfy a fixed-size invariant and is force-copied into a fixed buffer without a defensive length check at the point of use.

### Finding Description
The BLS public key length is produced upstream in `parse_extra`, which slices `remaining_data` using `VALIDATOR_BYTES_LENGTH` chunks per validator: [3](#0-2) . `VALIDATOR_BYTES_LENGTH` is a constant, and `bls_public_key.copy_from_slice(&bls_public_key_bytes)` at line 172 already assumes the slice is exactly 48 bytes (that copy itself would panic on any layout mismatch, e.g. a future BSC header format/testnet variant with a different `VALIDATOR_BYTES_LENGTH`/vote-attestation encoding, or a validator entry whose fields are shifted by a malformed but RLP-decodable `VoteAttestationData`). The consumer in `verifier/src/lib.rs` then re-derives `BlsPublicKey` from `val.bls_public_key.as_slice()` and calls `.expect("Infallible")`, asserting — without checking — that the length is always exactly 48. Both `update.source_header` (whose `extra_data` is attacker/relayer-controlled RLP) and `update.epoch_header_ancestry` (fully relayer-supplied headers) feed this path, so the "infallible" assumption is enforced only by the header's internal self-consistency, not by an explicit runtime check at the point where the invariant is actually relied upon.

### Impact Explanation
`verify_bsc_header` runs in the BSC light-client consensus update path, which is dispatched via `pallet-ismp`'s unsigned `handle_unsigned` extrinsic (`ismp::messaging::ConsensusMessage`) — reachable by any unprivileged relayer submitting a consensus proof, with no permission gate (`ensure_none(origin)` only). A panic inside consensus-message handling during `Self::execute(messages)` would abort transaction execution non-gracefully in a way not modeled as an `Err` path; if triggered inside `validate_unsigned`/`execute`, this can disrupt the BSC consensus client's ability to advance state (a route unable to deliver/verify messages), which blocks all Post/Get/Response/Timeout messages relying on that consensus state until a runtime upgrade — a form of the "route unable to deliver messages" impact class.

### Likelihood Explanation
The likelihood of an attacker being able to construct a validator-bytes slice with `len() != 48` while still passing all earlier `parse_extra` bounds checks is currently unclear: `VALIDATOR_BYTES_LENGTH` is a fixed constant, and the copy in `primitives.rs:172` would itself panic first if the slice length were wrong for the *current* format, meaning today's code paths make it hard to distinguish this specific `expect("Infallible")` as independently exploitable versus latent/defense-in-depth. I could not find a concrete relayer-controlled input that produces a definitively wrong-length key at this exact `try_into()` without already tripping the earlier `copy_from_slice`, so likelihood should be treated as uncertain pending closer analysis of all `VoteAttestationData`/RLP edge cases (e.g. truncated validator lists, alternate encodings across future BSC hard forks).

### Recommendation
Replace both `.as_slice().try_into().expect("Infallible")` calls in `modules/consensus/bsc/verifier/src/lib.rs` (lines 172 and 191) with a proper length check that returns `Error::InvalidBlsKeyLength` (or similar) instead of panicking, mirroring the defensive pattern already used elsewhere in the codebase (e.g. `modules/consensus/pharos/verifier/src/state_proof.rs`'s `Error::InvalidBlsKeyLength` checks, and the `ByteVector<N>` length-checked decode in `modules/utils/bls-utils/src/ssz/byte_vector.rs`). This removes the panic surface regardless of whether current constants make it reachable today.

### Proof of Concept
Not conclusively demonstrated: constructing a `BscClientUpdate` whose `epoch_header_ancestry[0]` or `source_header` yields a `ValidatorInfo::bls_public_key` of length ≠ 48 requires bypassing the fixed-size `copy_from_slice` in `parse_extra` (`primitives.rs:172`), which itself panics on a length mismatch under the current `VALIDATOR_BYTES_LENGTH`/RLP layout. A full PoC would require identifying either (a) a distinct code path where `ValidatorInfo` is constructed without that guard, or (b) a way to vary `VALIDATOR_BYTES_LENGTH`/validator entry width per BSC hard fork that this parser doesn't yet account for — neither of which was confirmed within the available context.

### Citations

**File:** modules/consensus/bsc/verifier/src/lib.rs (L169-173)
```rust
            let validators = epoch_header_extra_data
                .validators
                .into_iter()
                .map(|val| val.bls_public_key.as_slice().try_into().expect("Infallible"))
                .collect::<Vec<BlsPublicKey>>();
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L188-192)
```rust
            let validators = epoch_header_extra_data
                .validators
                .into_iter()
                .map(|val| val.bls_public_key.as_slice().try_into().expect("Infallible"))
                .collect::<Vec<BlsPublicKey>>();
```

**File:** modules/consensus/bsc/verifier/src/primitives.rs (L159-173)
```rust
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

```
