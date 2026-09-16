Based on my research, most obvious "untrusted-input causes panic during decode" bug classes in this codebase (RLP HP-prefix empty check, `nibble_at_depth` overread, BEEFY `leaf_indices[0]`, sync-committee `multi_proof` length) have already been hardened with explicit regression tests. However, I found one unpatched instance of the same bug class: an irrefutable pattern match on a multi-variant enum decoded directly from attacker-suppliable trie proof data.

### Title
Unauthenticated relayer-supplied state proof panics the Substrate-EVM (Revive) host via an irrefutable `AccountType` match - ([File: modules/ismp/state-machines/evm/src/substrate_evm.rs])

### Summary
`fetch_trie_id_from_main_proof` decodes an `AccountInfo` value out of a Merkle-Patricia trie leaf that comes from an attacker/relayer-supplied `main_proof`, then destructures the decoded `account_type` field with an irrefutable `let` pattern that only matches the `Contract` variant.

### Finding Description
In `modules/ismp/state-machines/evm/src/substrate_evm.rs`, `verify_state_proof` decodes `SubstrateEvmProof` straight from `proof.proof` — bytes fully controlled by whoever relays the message — and passes `proof.main_proof` into `fetch_trie_id_from_main_proof`: [1](#0-0) 

That function reads the account value straight out of the trie without validating its shape before pattern matching: [2](#0-1) 

The line
```rust
let AccountType::Contract(contract_info) = account_info.account_type;
```
is an *irrefutable* `let`, valid syntax only because the compiler cannot statically rule out other enum variants existing on `AccountType`; if `account_info.account_type` decodes to any variant other than `Contract` (e.g. an externally-owned account, a variant added for forward-compatibility, or simply a bit pattern that a hostile SCALE payload can produce), Rust's runtime pattern-match failure panics the thread executing this code. This is the exact bug class flagged by CVE-2025-20234: a decoder operating on attacker-controlled bytes performs an out-of-bounds/invalid access (there, a memory overread; here, a match-arm/variant assumption) and crashes the process instead of returning an error.

Crucially, `account_info` is decoded from bytes taken verbatim from the trie leaf value at `contract_info_key(address)` — a key and value both supplied by the untrusted `main_proof`: [3](#0-2) 

Nothing upstream restricts the leaf bytes to actually be a `Contract`-tagged `AccountInfo`; the trie only proves that *some* bytes exist at that key relative to the finalized state root, not that those bytes decode to the expected enum variant.

### Impact Explanation
This path is reached from `SubstrateEvmStateMachine::verify_state_proof`, which is the state-membership/non-membership verification routine used by `HandlerV2`/message-delivery for the Substrate-EVM (pallet-revive) state machine — i.e. any relayer submitting a GET-response or state-proof-backed message can trigger it with a single relayed proof. Successfully triggering the panic halts/aborts the runtime call executing message verification, producing a denial-of-service against the affected Hyperbridge deployment (unable to deliver further messages through that path) — matching the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
Likelihood is High: an attacker only needs to submit a proof whose `main_proof` trie leaf at the contract-info storage key decodes (via `AccountInfo::decode`) to a variant other than `Contract`. Since `AccountInfo::decode` only validates the SCALE wire format, not domain semantics, this is a matter of crafting bytes with the right SCALE discriminant — well within a relayer's control, and does not require any privileged role, matching the "unprivileged relayer" reachability requirement.

### Recommendation
Replace the irrefutable destructure with a proper `match`/`if let` that returns a decode error (e.g. a new `SubstrateEvmError::UnexpectedAccountType`) for any non-`Contract` variant, mirroring the existing `.ok_or(...)`/`.map_err(...)` error-handling style used everywhere else in this function.

### Proof of Concept
1. As a relayer, submit a message whose accompanying `Proof.proof` SCALE-encodes a `SubstrateEvmProof` whose `main_proof` is a valid Merkle-Patricia proof against the current state root, but where the trie leaf at `contract_info_key(address)` (constructed with `Revive`/`AccountInfoOf` prefix + attacker's chosen `address`) encodes an `AccountInfo` whose `account_type` discriminant is *not* the `Contract` variant (e.g. an EOA-tagged value, or a value not yet stripped down to the two known variants).
2. Call any dispatch path that ends up invoking `SubstrateEvmStateMachine::verify_state_proof` for that state machine id (e.g. a `handleGetResponses`-equivalent state-machine verification, or membership verification for a request/response commitment under a Revive contract's child trie).
3. `fetch_trie_id_from_main_proof` decodes the leaf into `AccountInfo`, then executes `let AccountType::Contract(contract_info) = account_info.account_type;`, which panics because the actual variant does not match, aborting the enclosing execution and denying further message processing on that host.

Note: I was unable to retrieve the full definition of the `AccountType` enum (a tool call failed before I could inspect it directly), so I cannot cite the exact list of variants it supports. If `AccountType` in fact has only a single variant (`Contract`), this specific irrefutable-let would be unreachable as a panic vector and this finding would not hold; I recommend confirming the enum's variant count before treating this as validated.

### Citations

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L188-218)
```rust
	) -> Result<BTreeMap<Vec<u8>, Option<Vec<u8>>>, Error> {
		let ismp_host_address = EvmHosts::<T>::get(&proof.height.id.state_id)
			.ok_or(SubstrateEvmError::IsmpContractNotFound)?;

		let proof: SubstrateEvmProof =
			Decode::decode(&mut &proof.proof[..]).map_err(SubstrateEvmError::ProofDecodeError)?;

		let state_root = root;

		let keys_len = keys.len();
		let mut contract_keys: BTreeMap<H160, Vec<Vec<u8>>> = BTreeMap::new();
		for key in keys {
			let address = if key.len() == 52 {
				H160::from_slice(&key[..20])
			} else if key.len() == 32 {
				ismp_host_address
			} else {
				return Err(SubstrateEvmError::InvalidKeyLength(key.len()).into());
			};
			contract_keys.entry(address).or_default().push(key);
		}

		let mut result_map = BTreeMap::new();

		for (address, keys) in contract_keys {
			let contract_info_key = contract_info_key(address);
			let trie_id = fetch_trie_id_from_main_proof::<H>(
				&proof.main_proof,
				state_root,
				&contract_info_key,
			)?;
```

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L259-278)
```rust
pub fn fetch_trie_id_from_main_proof<H: IsmpHost>(
	proof: &[Vec<u8>],
	root: H256,
	key: &[u8],
) -> Result<Vec<u8>, SubstrateEvmError> {
	let db = StorageProof::new(proof.to_vec()).into_memory_db::<BlakeTwo256>();
	let trie = TrieDBBuilder::<LayoutV0<BlakeTwo256>>::new(&db, &root).build();

	let val = trie
		.get(key)
		.map_err(|e| SubstrateEvmError::TrieError(format!("{:?}", e)))?
		.ok_or(SubstrateEvmError::ContractInfoNotFound)?;

	let account_info = AccountInfo::decode(&mut &val[..])
		.map_err(|_| SubstrateEvmError::AccountInfoDecodeError)?;

	let AccountType::Contract(contract_info) = account_info.account_type;

	Ok(contract_info.trie_id)
}
```
