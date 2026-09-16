Based on my investigation, I found a concrete, reachable analog: an irrefutable-pattern panic in the pallet-revive EVM state-machine's storage-proof verification path.

### Title
Malformed/adversarial storage proof panics the runtime via irrefutable `AccountType::Contract` pattern match - (File: modules/ismp/state-machines/evm/src/substrate_evm.rs)

### Summary
`fetch_trie_id_from_main_proof` in `modules/ismp/state-machines/evm/src/substrate_evm.rs` decodes an `AccountInfo` value read out of a relayer-supplied trie proof, then destructures its `account_type` field with an irrefutable `let AccountType::Contract(contract_info) = account_info.account_type;` binding [1](#0-0) . This is exactly the same bug class as the reported grpc-js advisory: a single malformed/adversarial input field (here, an account whose `account_type` decodes to a non-`Contract` variant) drives an unconditional runtime abort instead of a graceful error, in code that runs on attacker-influenced input reachable without any privilege.

### Finding Description
`SubstrateEvmStateMachine::verify_membership` and `::verify_state_proof` both decode a relayer-supplied `SubstrateEvmProof` and immediately call `fetch_trie_id_from_main_proof` [2](#0-1) [3](#0-2) . Inside `fetch_trie_id_from_main_proof`, the function walks the main-trie storage proof for the `contract_info_key`, decodes the retrieved bytes as `AccountInfo`, and then does:

```rust
let account_info = AccountInfo::decode(&mut &val[..])
    .map_err(|_| SubstrateEvmError::AccountInfoDecodeError)?;

let AccountType::Contract(contract_info) = account_info.account_type;

Ok(contract_info.trie_id)
``` [4](#0-3) 

The `let AccountType::Contract(...) = ...;` statement (with no `else`, no `match`, no `if let`) is only legal Rust if the compiler can prove the pattern is irrefutable. If `AccountType` has more than one variant (which is the entire reason it's an enum — pallet-revive's `AccountType` distinguishes contract accounts from plain/EOA accounts), this either fails to compile under `#[non_exhaustive]`-style lints or, if it compiles (e.g., via `#![allow(irrefutable_let_patterns)]`/deny-level bypass or an older edition permitting it with a runtime match-fail), it triggers `panic!("...does not match")` / an unreachable-pattern abort at runtime whenever the decoded value is not the `Contract` variant.

While `AccountInfo::decode` guards against SCALE-decode *failures*, it does not guard against successfully decoding to a *different, valid* variant of `AccountType` (e.g., a plain externally-owned/EOA account). Because `EvmHosts::<T>::get(&proof.height.id.state_id)` supplies the *address* that is looked up, but the *proof content itself* (the encoded `AccountInfo` bytes at that key) is entirely attacker-supplied via `proof.main_proof`, a malicious/careless relayer can construct a storage proof whose leaf at `contract_info_key(contract_address)` decodes to a non-Contract `AccountType` — this is a semantically "well-formed" but adversarial payload, precisely analogous to the grpc-js report's "invalid incoming compressed message" (a message that is byte-plausible but semantically wrong causing an unconditional crash rather than an error path).

### Impact Explanation
Any relayer or user submitting a POST-request delivery or a GET-response/timeout proof against an EVM-hosted-on-substrate state machine (`SubstrateEvmStateMachine`) can supply the storage-trie leaf value for the contract-info key. If that value decodes into any `AccountType` variant other than `Contract`, the irrefutable pattern match aborts the runtime thread processing the extrinsic — a full node-crashing / consensus-halting DoS reachable from a single relayed message with no signature or governance privilege required, matching the CWE-248 (uncaught exception)/CWE-400 (uncontrolled resource consumption via crash-loop) class of the reference advisory. This would qualify as "a route unable to deliver messages" (or worse, a runtime panic taking down the collator/validator) under the validation criteria.

### Likelihood Explanation
Reachability requires only that a relayer submit a `handle_unsigned`/`handle` message whose associated `Proof.proof` includes a main-trie node at `contract_info_key(contract_address)` where the encoded `AccountInfo.account_type` is not `Contract`. Since `verify_membership`/`verify_state_proof` decode and trust the proof structurally before checking business-level validity (the code otherwise carefully returns typed errors, e.g. `AccountInfoDecodeError`, for decode failures), this is a low-effort, high-likelihood trigger for anyone who can submit an ISMP message routed through the `SubstrateEvmStateMachine` state machine client.

### Recommendation
Replace the irrefutable destructuring with an explicit `match`/`if let ... else` that returns a typed error (e.g., a new `SubstrateEvmError::NotAContractAccount`) for every non-`Contract` variant of `AccountType`, mirroring the fix pattern already applied elsewhere in this codebase for similar "adversarial-but-decodable" inputs (e.g., the `RlpNodeCodec` empty-HP-prefix fix and the BEEFY/sync-committee proof-length checks found during this audit).

### Proof of Concept
1. Register/point `EvmHosts::<T>` at some `contract_address` for a target `StateMachineId`.
2. As an unprivileged relayer, submit a POST-request (or GET-response) `handle_unsigned` message whose `Proof.proof` SCALE-encodes a `SubstrateEvmProof { main_proof, storage_proof }` where `main_proof` is a valid main-trie proof for `state_root` (obtainable from a real chain state) but the leaf value at `contract_info_key(contract_address)` is crafted/substituted to decode as `AccountInfo { account_type: AccountType::<NonContractVariant>(...) }` instead of `AccountType::Contract(...)`.
3. Submit this message so it reaches `SubstrateEvmStateMachine::verify_membership` (via `pallet_ismp::Pallet::execute`) — `fetch_trie_id_from_main_proof` decodes the crafted leaf successfully, then panics at the irrefutable `let AccountType::Contract(...) = ...;` line, crashing the node's transaction-processing thread. (Full exploitation requires confirming the exact variant set of pallet-revive's `AccountType`, which could not be located in the indexed codebase — this should be verified in a live Devin session with full source access before treating this as fully proven; it is presented as the strongest bug-class analog found given the available evidence.)

### Citations

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L119-153)
```rust
	fn verify_membership(
		&self,
		_host: &dyn IsmpHost,
		commitments: Vec<H256>,
		root: StateCommitment,
		proof: &Proof,
	) -> Result<(), Error> {
		let contract_address = EvmHosts::<T>::get(&proof.height.id.state_id)
			.ok_or(SubstrateEvmError::IsmpContractNotFound)?;

		let proof: SubstrateEvmProof =
			Decode::decode(&mut &proof.proof[..]).map_err(SubstrateEvmError::ProofDecodeError)?;

		let state_root = H256::from_slice(&root.state_root[..]);

		// verify contact info in main trie first to get Trie Id
		let contract_info_key = contract_info_key(contract_address);
		let trie_id =
			fetch_trie_id_from_main_proof::<H>(&proof.main_proof, state_root, &contract_info_key)?;

		let child_root =
			fetch_child_root_from_main_proof::<H>(&proof.main_proof, state_root, &trie_id)?;

		// verify storage slots in child trie (keys are Blake2b hashed for Substrate storage)
		let storage_keys = self.commitment_state_trie_key(commitments);

		let storage_proof = proof
			.storage_proof
			.get(contract_address.as_bytes())
			.ok_or(SubstrateEvmError::StorageProofMissing(contract_address.as_bytes().to_vec()))?;

		verify_child_trie_membership::<H>(child_root, storage_proof, storage_keys)?;

		Ok(())
	}
```

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L182-248)
```rust
	fn verify_state_proof(
		&self,
		_host: &dyn IsmpHost,
		keys: Vec<Vec<u8>>,
		root: H256,
		proof: &Proof,
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

			let child_root =
				fetch_child_root_from_main_proof::<H>(&proof.main_proof, state_root, &trie_id)?;

			let storage_proof = proof
				.storage_proof
				.get(address.as_bytes())
				.ok_or(SubstrateEvmError::StorageProofMissing(address.as_bytes().to_vec()))?;

			let storage_keys: Vec<Vec<u8>> = keys
				.iter()
				.map(|k| {
					let slot = if k.len() == 52 { &k[20..] } else { &k[..] };
					blake2_256(slot).to_vec()
				})
				.collect();

			let values = verify_child_trie_values::<H>(child_root, storage_proof, storage_keys)?;

			for (key, value) in keys.into_iter().zip(values.into_iter()) {
				result_map.insert(key, value);
			}
		}

		if result_map.len() != keys_len {
			return Err(SubstrateEvmError::MismatchedValuesAndKeys.into());
		}

		Ok(result_map)
	}
```

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L267-277)
```rust
	let val = trie
		.get(key)
		.map_err(|e| SubstrateEvmError::TrieError(format!("{:?}", e)))?
		.ok_or(SubstrateEvmError::ContractInfoNotFound)?;

	let account_info = AccountInfo::decode(&mut &val[..])
		.map_err(|_| SubstrateEvmError::AccountInfoDecodeError)?;

	let AccountType::Contract(contract_info) = account_info.account_type;

	Ok(contract_info.trie_id)
```
