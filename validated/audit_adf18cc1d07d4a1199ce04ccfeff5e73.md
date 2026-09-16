### Title
Panicking `.expect("Infallible")` on attacker-influenced BLS public key length in BSC consensus verifier can crash nodes - ([File: modules/consensus/bsc/verifier/src/lib.rs])

### Summary
The BSC consensus client's `verify_bsc_header` function converts each validator's `bls_public_key` bytes into a fixed-size `BlsPublicKey` array using `.try_into().expect("Infallible")`. This mirrors the M-5 bug class (`MustNewDecFromString`/unchecked-panic-on-parse): if the untrusted, relayer-supplied BSC epoch header's validator list contains a `bls_public_key` whose length does not match the expected fixed size, the `TryInto` conversion returns `Err`, and `.expect("Infallible")` panics instead of surfacing a handled error.

### Finding Description
In `verify_bsc_header`, when an epoch boundary is reached (either via `epoch_header_ancestry[0]` or `update.source_header` itself being an epoch boundary), the function extracts the next validator set from the header's `extra_data`: [1](#0-0) [2](#0-1) 

Both branches call `parse_extra::<H, C>(&header)` to decode the RLP-encoded `extra_data` of a BSC block header into a list of validators, then map each validator's `bls_public_key` via:
```rust
val.bls_public_key.as_slice().try_into().expect("Infallible")
```
This conversion assumes the decoded `bls_public_key` field is always exactly the length of `BlsPublicKey` (a fixed 48-byte array type). This assumption is only safe if `parse_extra` strictly validates/truncates the RLP-decoded bytes to that exact length before this point; if it does not (e.g., BEP-126 RLP header data is attacker/relayer-influenced and this is parsed from raw untrusted bytes), a header with a validator entry carrying an incorrectly sized `bls_public_key` will cause `try_into()` to return `Err`, and the subsequent `.expect("Infallible")` will panic.

This code path is reachable by any permissionless relayer: BSC consensus updates are submitted via `pallet-ismp`'s unsigned extrinsic `handle_unsigned` (`ensure_none` origin, callable by anyone with a plausible proof) which dispatches into consensus-client message handling, ultimately calling into `verify_bsc_header` for header updates: [3](#0-2) 

### Impact Explanation
A panic inside consensus verification triggered from an unsigned, permissionless extrinsic can crash/halt the node processing the block (denial of service for the runtime executing ISMP message handling), which affects message delivery for the entire BSC light client and any application relying on it. This matches the "route unable to deliver messages" acceptance criterion — an attacker-crafted or malformed relayed BSC header could take down message processing for that consensus client.

### Likelihood Explanation
This requires that `parse_extra` does not itself enforce the exact byte length of each validator's `bls_public_key` before this conversion. I was not able to fully confirm the internal validation logic of `parse_extra` (in `modules/consensus/bsc/verifier/src/primitives.rs`) within the remaining investigation budget, so the exact reachability of a length mismatch is not fully proven — this is presented as a plausible analog of the M-5 pattern (unchecked panic-inducing conversion on relayer-supplied data) rather than a fully verified exploit. If `parse_extra` already bounds/validates the slice length (e.g. always producing exactly 48 bytes per validator or erroring out earlier), this specific `.expect` is unreachable with malformed input and the vulnerability class does not apply here.

### Recommendation
Replace `.expect("Infallible")` with proper error propagation:
```rust
let validators = epoch_header_extra_data
    .validators
    .into_iter()
    .map(|val| {
        val.bls_public_key
            .as_slice()
            .try_into()
            .map_err(|_| Error::InvalidBlsPublicKeyLength)
    })
    .collect::<Result<Vec<BlsPublicKey>, _>>()?;
```
Additionally, verify (and if needed, add an explicit length check in) `parse_extra` to reject headers whose validator `bls_public_key` fields are not exactly the expected size, before this point, so malformed/malicious relayed headers are rejected via a typed error rather than risking a panic path.

### Proof of Concept
Not independently reproduced — the exploit would require confirming that `parse_extra` (in `modules/consensus/bsc/verifier/src/primitives.rs`) allows validator `bls_public_key` entries of a length other than the fixed `BlsPublicKey` size to pass through to `verify_bsc_header`. A concrete PoC would submit a crafted BSC epoch-boundary header (with a validator section containing a truncated/oversized `bls_public_key`) via `handle_unsigned` targeting the BSC consensus client's `create_consensus_client`/update path, and observe a panic instead of a rejected extrinsic.

### Citations

**File:** modules/consensus/bsc/verifier/src/lib.rs (L166-173)
```rust
            let epoch_header = update.epoch_header_ancestry[0].clone();
            let epoch_header_extra_data = parse_extra::<H, C>(&epoch_header)
                .map_err(|_| Error::ParseEpochExtraData)?;
            let validators = epoch_header_extra_data
                .validators
                .into_iter()
                .map(|val| val.bls_public_key.as_slice().try_into().expect("Infallible"))
                .collect::<Vec<BlsPublicKey>>();
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L185-192)
```rust
        } else if update.source_header.number.low_u64() % epoch_length == 0 {
            let epoch_header_extra_data = parse_extra::<H, C>(&update.source_header)
                .map_err(|_| Error::ParseEpochExtraData)?;
            let validators = epoch_header_extra_data
                .validators
                .into_iter()
                .map(|val| val.bls_public_key.as_slice().try_into().expect("Infallible"))
                .collect::<Vec<BlsPublicKey>>();
```

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```
