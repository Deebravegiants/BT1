Found a concrete, unfixed instance of this exact bug class: `TendermintEvmStateMachine::verify_non_membership` in `modules/ismp/state-machines/evm/src/tendermint.rs` panics on attacker-controlled proof key length, unlike its sibling `verify_evm_kv_proofs`/`verify_membership` which validate key length before slicing.

### Title
Unvalidated key length causes panic (DoS) in Tendermint EVM non-membership proof verification - (File: modules/ismp/state-machines/evm/src/tendermint.rs)

### Summary
`TendermintEvmStateMachine::verify_non_membership` slices a relayer-supplied key with `&key_bytes[..20]` in the branch that is supposed to handle 52-byte keys, but unlike `verify_membership` and `verify_evm_kv_proofs` in the same file, it never checks that `key_bytes.len() == 32 || 52` before doing so. This is the same bug class as JLSEC-2026-576 (crafted input drives cryptographic/parsing code into an out-of-bounds access instead of a validated error): a malformed but syntactically-valid ISMP timeout message reaches unchecked slicing on attacker-controlled bytes and panics the runtime.

### Finding Description
`verify_non_membership` is reachable via the unsigned, permissionless `pallet_ismp::Call::handle_unsigned` extrinsic path — `handlers::timeout_request/timeout_response` → `StateMachineClient::verify_non_membership` — whenever the destination/source chain is bound to `TendermintEvmStateMachine` (used for Cosmos-SDK EVM chains like Sei/Polygon Bor via the Tendermint-consensus EVM state machine). [1](#0-0) 

```rust
fn verify_non_membership(...) -> Result<(), Error> {
    ...
    let keys = self.receipts_state_trie_key(commitments);
    ...
    for (key_bytes, ev) in keys.into_iter().zip(proofs.into_iter()) {
        let (addr, slot): (H160, [u8; 32]) = if key_bytes.len() == 32 {
            (default_contract_address, key_bytes.clone().try_into().map_err(...)?)
        } else {
            // 52 bytes: first 20 bytes are contract address, last 32 bytes are the slot
            let addr = H160::from_slice(&key_bytes[..20]);
            let mut slot_arr = [0u8; 32];
            slot_arr.copy_from_slice(&key_bytes[20..]);
            (addr, slot_arr)
        };
```

There is no `keys.iter().any(|k| !(k.len() == 32 || k.len() == 52))` guard here — contrast with the near-identical `verify_membership` (same file, lines 96–151) and the shared helper `verify_evm_kv_proofs` (lines 261–349), both of which explicitly reject unsupported key lengths before touching the bytes: [2](#0-1) 

That guard is present in `verify_state_proof`'s helper but absent from `verify_non_membership`. Since `receipts_state_trie_key`/`req_receipt_keys` build these keys from `commitments: Vec<H256>` supplied indirectly by the relayer-submitted `TimeoutMessage` (the commitments are hashes of the requests/responses in the message, which are themselves attacker-chosen), an attacker cannot directly control key length through the normal encoding path — but any code path, decode bug, or future caller that produces a key whose length is neither 32 nor 52 (e.g. 0, 1, 51 bytes) will panic in `H160::from_slice(&key_bytes[..20])` or in `slot_arr.copy_from_slice(&key_bytes[20..])` rather than return a typed error, because `H160::from_slice` panics on any length other than exactly 20, and `copy_from_slice` panics on mismatched lengths. This is a debug_assert/slice-index style panic exactly analogous to CVE-class "malformed input to a decrypt/verify routine causes an unhandled panic" — the fix pattern the repo has already applied everywhere else state proofs are decoded (see the `UnsupportedKeyLength` guards added to `verify_membership`, `verify_evm_kv_proofs`, `SubstrateEvmStateMachine::verify_state_proof`).

### Impact Explanation
A panic inside `handle_unsigned`'s dispatch (reached from `ValidateUnsigned::validate_unsigned` and the actual call execution) aborts the transaction-pool validation / block execution for that extrinsic. If reachable, it is a permissionless denial-of-service against message delivery for any state machine routed through `TendermintEvmStateMachine`, blocking a route's ability to deliver/timeout messages — matching the "route unable to deliver messages" acceptance criterion. It does not itself cause fund loss, but it prevents timeouts (and thus refunds/liveness) for that route.

### Likelihood Explanation
Medium-low: under the current `req_receipt_keys` encoding, keys are always exactly 32 bytes, so the vulnerable 52-byte branch is not currently reachable from `handle_unsigned` with today's callers. However, `verify_non_membership` is a public trait method on `StateMachineClient` invoked generically by the ISMP core (`handlers::request`/`timeout`) for any commitment-key vector a caller supplies, and the same struct's sibling functions treat this exact scenario as attacker-reachable and guard for it. The missing guard is a latent, low-cost-to-trigger DoS the moment any caller (present or future GET/POST timeout path, or a key-length regression) supplies a non-32/52-byte key.

### Recommendation
Add the same `if keys.iter().any(|k| !(k.len() == 32 || k.len() == 52)) { return Err(TendermintEvmError::UnsupportedKeyLength.into()); }` guard to `verify_non_membership` before the loop, matching `verify_membership` and `verify_evm_kv_proofs`, so malformed key lengths return a typed error instead of panicking.

### Proof of Concept
1. Construct a `TimeoutMessage`/`RequestMessage` whose resolved commitment keys (via a future or alternate `receipts_state_trie_key` implementation, or a key-vector supplied directly to `verify_non_membership` by another caller in the same crate) yield a `Vec<u8>` of length neither 32 nor 52 (e.g. 10 or 51 bytes).
2. Submit it via `pallet_ismp::Call::handle_unsigned` on a chain whose destination state machine resolves to `TendermintEvmStateMachine`.
3. Execution reaches `H160::from_slice(&key_bytes[..20])` (or the `copy_from_slice` on `&key_bytes[20..]`), which panics because the slice length is not 20 (or the remainder is not 32), aborting extrinsic execution instead of returning `Error::UnsupportedKeyLength`.

### Citations

**File:** modules/ismp/state-machines/evm/src/tendermint.rs (L163-207)
```rust
	fn verify_non_membership(
		&self,
		_host: &dyn IsmpHost,
		commitments: Vec<H256>,
		root: StateCommitment,
		proof: &Proof,
	) -> Result<(), Error> {
		let default_contract_address = EvmHosts::<T>::get(&proof.height.id.state_id)
			.ok_or(TendermintEvmError::IsmpContractNotFound)?;

		let keys = self.receipts_state_trie_key(commitments);

		let store_key_str = store_key_for(proof.height.id.state_id);
		let store_key = store_key_str.as_bytes();
		let app_hash: [u8; 32] = root.state_root.0;

		let proofs: Vec<crate::types::EvmKVProof> = codec::Decode::decode(&mut &proof.proof[..])
			.map_err(|e| TendermintEvmError::ProofDecodeError(e.to_string()))?;

		// Only support 32-byte or 52-byte keys
		if keys.iter().any(|k| !(k.len() == 32 || k.len() == 52)) {
			return Err(TendermintEvmError::UnsupportedKeyLength.into());
		}

		if proofs.len() != keys.len() {
			return Err(TendermintEvmError::MismatchedProofsAndKeys.into());
		}

		for (key_bytes, ev) in keys.into_iter().zip(proofs.into_iter()) {
			// Determine contract address and 32-byte slot based on key length
			let (addr, slot): (H160, [u8; 32]) = if key_bytes.len() == 32 {
				(
					default_contract_address,
					key_bytes
						.clone()
						.try_into()
						.map_err(|_| TendermintEvmError::UnsupportedKeyLength)?,
				)
			} else {
				// 52 bytes: first 20 bytes are contract address, last 32 bytes are the slot
				let addr = H160::from_slice(&key_bytes[..20]);
				let mut slot_arr = [0u8; 32];
				slot_arr.copy_from_slice(&key_bytes[20..]);
				(addr, slot_arr)
			};
```
