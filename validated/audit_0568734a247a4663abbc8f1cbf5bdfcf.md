### Title
`req_receipt_keys` addresses `_requestReceipts[commitment]` at offset 0, which can be zero-valued for a legitimately delivered request, letting EVM's absent-vs-zero storage ambiguity forge a non-membership (timeout) proof for a delivered request - (File: modules/ismp/state-machines/evm/src/utils.rs)

### Summary
The external report's root cause is a boundary condition where a computation implicitly treats a real, in-range value as if it were "unset" (zero), which an attacker exploits to make the protocol accept a state it should have rejected (draining reserves). The same class of bug — EVM's inability to distinguish an explicitly-stored zero from an absent storage slot — is architecturally acknowledged in this codebase for `RequestCommitments` (offset 1, "sender", is deliberately used instead of offset 0, "fee", specifically "because membership verification needs an always-non-zero slot — EVM returns a non-membership proof for zero-valued slots"), but `req_receipt_keys` for `RequestReceipts` was not given the same treatment: it points at offset 0 without any non-zero-field guarantee.

### Finding Description
`modules/pallets/relayer/src/accumulate.rs` explicitly documents the underlying hazard: [1](#0-0) 

This is precisely the reported bug class: on Ethereum's Merkle-Patricia trie, a storage slot holding the value `0` is indistinguishable from a slot that was never written — both produce a valid *non-existence* proof. The developers correctly worked around this for `commitment_state_trie_key` by targeting the `sender` field (guaranteed non-zero, since every real request has a sender) instead of `fee` (which legitimately can be zero): [2](#0-1) 

However, `req_receipt_keys` — used by `receipts_state_trie_key`, which backs `verify_non_membership` (the mechanism the ISMP timeout handler uses to prove a request was *never delivered*) — derives its key at offset 0 with no analogous non-zero-field selection: [3](#0-2) 

This key is consumed directly in `verify_non_membership`, which treats "no value returned" as proof of non-delivery: [4](#0-3) 

If the EVM `IsmpHost`'s `_requestReceipts[commitment]` mapping stores the relayer/receipt data such that the word at offset 0 can legitimately be `0` for a request that **was** actually delivered (e.g., a struct field ordering where offset 0 is not always non-zero, or any receipt encoding whose first word can be zero for a valid entry), then a relayer/attacker could construct (or simply happen to possess) a state proof where `get_value_from_proof` returns `None` for that slot even though the request was delivered — exactly mirroring how `Gaussian.ppf` was silently zeroed at `x=0`/`x=1e18` instead of correctly evaluating to ±infinity. The verifier's `if values.into_iter().any(|(_key, val)| val.is_some())` bounds check never fires, `verify_non_membership` returns `Ok(())`, and a `PostRequestTimeoutMessage`/`GetTimeoutMessage` is accepted for a request that was in fact fulfilled.

### Impact Explanation
Accepting a forged non-membership (timeout) proof for an already-delivered ISMP request lets the source-chain dispatcher refund/unlock the escrowed input funds to the original sender via the timeout path, while the destination-side fill has already paid out the counterparty — a double-spend that drains bridge/escrow reserves, matching the "steal all pool reserves" impact class of the original report (concrete theft of funds via a forged/undetectable boundary condition in a security-critical verification path).

### Likelihood Explanation
This requires the receipt storage layout to actually admit a legitimate zero at the queried offset — I was not able to fully confirm the exact Solidity struct layout of `_requestReceipts` in the available index (the `IHost`/`EvmHost.sol` receipt struct fields were not retrievable in this session), so whether offset 0 can be non-zero-guaranteed by construction (e.g., if it stores the relayer address, which is never `address(0)` for a genuine delivery) is **unconfirmed**. If it does hold such a guarantee, this specific path is safe by accident rather than by explicit design (unlike the commitment path, which has an explicit, documented non-zero-field choice); if any future refactor changes the receipt struct field order or adds an optional/zeroable leading field, this class of bug reappears with no test or invariant currently guarding against it.

### Recommendation
- Verify and document (as already done for `commitment_state_trie_key`) that the field targeted by `req_receipt_keys`/`REQUEST_RECEIPTS_SLOT` offset 0 is provably non-zero for every genuinely delivered request (e.g., pin it to the relayer address field, never `fee` or a nullable value), and add an explicit offset parameter mirroring `req_commitment_key`'s design rather than leaving offset 0 implicit.
- Add a regression test asserting that `verify_non_membership` rejects a proof where the destination receipt slot is present-but-zero-valued (simulate via a crafted proof), the same way membership tests exist for zero-valued commitment slots.
- Audit all other `derive_unhashed_map_key`/`derive_unhashed_map_key_with_offset` call sites for whether the addressed field can legitimately be zero while the corresponding logical record still exists, since EVM's inability to prove "present but zero" is a systemic sharp edge, not a one-off bug.

### Proof of Concept
Conceptual PoC (blocked by the fact that the exact `_requestReceipts` struct layout on `EvmHost.sol` could not be confirmed in this session):
1. Identify (or arrange, if any field is attacker-influenced) a delivered request whose commitment's `_requestReceipts[commitment]` storage word at slot-offset 0 equals `0x0` (e.g., if that word encodes a sub-field that can naturally be zero, such as a packed flag/timestamp preceding the relayer address).
2. Obtain a standard `eth_getProof` non-existence proof for that exact storage slot — the EVM trie legitimately returns a valid Merkle non-inclusion proof for a zero-valued slot.
3. Submit this proof as the `Proof` in a `PostRequestTimeoutMessage`/`GetTimeoutMessage`; `verify_non_membership` decodes `values` as `None` for the key and returns `Ok(())}`, allowing the timeout handler to release source-chain escrow for a request that was already fulfilled on the destination chain.

### Citations

**File:** modules/pallets/relayer/src/accumulate.rs (L172-181)
```rust
	/// Derives the source-chain storage keys that hold the relayer fee for each request
	/// commitment in the batch.
	///
	/// EVM chains store request commitments as a `FeeMetadata { fee, sender }` struct in the
	/// `RequestCommitments` mapping. [`StateMachineClient::commitment_state_trie_key`] addresses
	/// the `sender` field (offset 1) because membership verification needs an always-non-zero
	/// slot — EVM returns a non-membership proof for zero-valued slots. Fee accumulation instead
	/// needs the `fee` field at offset 0, so for EVM sources the offset-0 slot is derived here
	/// directly rather than reusing the membership key.
	///
```

**File:** modules/ismp/state-machines/evm/src/utils.rs (L91-106)
```rust
pub fn req_commitment_key<H: Keccak256, F>(commitments: Vec<H256>, hash_fn: F) -> Vec<Vec<u8>>
where
	F: Fn(&[u8]) -> Vec<u8>,
{
	let mut keys = vec![];
	for commitment in commitments {
		let unhashed_key = derive_unhashed_map_key_with_offset::<H>(
			commitment.0.to_vec(),
			REQUEST_COMMITMENTS_SLOT,
			1,
		);
		keys.push(hash_fn(&unhashed_key.0))
	}

	keys
}
```

**File:** modules/ismp/state-machines/evm/src/utils.rs (L108-116)
```rust
pub fn req_receipt_keys<H: Keccak256>(commitments: Vec<H256>) -> Vec<Vec<u8>> {
	let mut keys = vec![];
	for commitment in commitments {
		let key = derive_unhashed_map_key::<H>(commitment.0.to_vec(), REQUEST_RECEIPTS_SLOT);
		keys.push(key.0.to_vec())
	}

	keys
}
```

**File:** modules/ismp/state-machines/evm/src/lib.rs (L304-321)
```rust
	fn verify_non_membership(
		&self,
		host: &dyn IsmpHost,
		commitments: Vec<H256>,
		root: StateCommitment,
		proof: &Proof,
	) -> Result<(), Error> {
		let keys = self.receipts_state_trie_key(commitments);
		let keys_len = keys.len();
		let values = self.verify_state_proof(host, keys, root.state_root, proof)?;
		if values.len() != keys_len {
			return Err(EvmStateMachineError::MismatchedValuesAndKeys.into());
		}
		if values.into_iter().any(|(_key, val)| val.is_some()) {
			return Err(EvmStateMachineError::DeliveredRequestsInBatch.into());
		}
		Ok(())
	}
```
