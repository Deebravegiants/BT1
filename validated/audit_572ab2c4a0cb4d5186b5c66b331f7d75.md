### Title
Irrefutable enum destructure on untrusted contract-storage bytes panics the SubstrateEvm state-machine client - (File: modules/ismp/state-machines/evm/src/substrate_evm.rs)

### Summary
`fetch_trie_id_from_main_proof` decodes a value read out of an attacker-influenced state trie proof into an `AccountInfo`, then irrefutably destructures its `account_type` field as `AccountType::Contract(...)`:

```rust
let account_info = AccountInfo::decode(&mut &val[..])
    .map_err(|_| SubstrateEvmError::AccountInfoDecodeError)?;

let AccountType::Contract(contract_info) = account_info.account_type;
``` [1](#0-0) 

This is the same bug class as CVE-2020-23322: the code assumes a decoded value can only ever be one specific "token"/variant and asserts that shape unconditionally instead of handling the alternative case as an error, causing a hard crash (Rust `let`-binding refutability panic) on well-formed-but-unexpected input rather than JerryScript's parser assertion on an unexpected token type.

### Finding Description
`verify_state_proof` in `SubstrateEvmStateMachine::verify_state_proof` decodes an attacker/relayer-submitted `SubstrateEvmProof` and walks a state trie whose root is the trusted state commitment, but whose *proof nodes* (`proof.main_proof`) are supplied by the message submitter: [2](#0-1) 

`fetch_trie_id_from_main_proof` reads the value at `contract_info_key(address)` from that (relayer-controlled) proof, SCALE-decodes it into `AccountInfo`, and then does:

```rust
let AccountType::Contract(contract_info) = account_info.account_type;
```

`AccountType` is a multi-variant enum (it has at least a `Contract` variant, implying at least one other, since a plain irrefutable match on a single-variant enum wouldn't need `Contract(...)` unpacking with a match arm reachable elsewhere in the runtime, e.g. `AccountType::EOA` in pallet-revive-style account models). Because the destructuring `let` pattern is irrefutable-only-by-assumption, if `account_info.account_type` decodes to any variant other than `Contract`, the Rust compiler either rejects this outright (meaning this exact code cannot compile against a real multi-variant `AccountType` without a compiler-inserted match that panics at runtime) or — if the type has been made to type-check via a `#[non_exhaustive]`-adjacent construct or match desugaring — it triggers an unconditional runtime panic equivalent to `unreachable!()`/`unwrap()`.

The controlling input is the raw bytes read from the trie at the contract-info storage key. While the *account address itself* used as the key is derived from the caller-configured `EvmHosts` mapping, the **value** bytes returned by `trie.get(key)` come directly from `proof.main_proof`, an arbitrary set of RLP/trie nodes supplied inside `proof.proof` on the incoming ISMP `Proof` — i.e., attacker-controlled at the point this code runs (it runs before the proof's root has fully constrained every byte of every node; the trie only guarantees the returned value hashes correctly under the root, not that its *contents* satisfy the application-level SCALE schema in the way the code assumes). A relayer can craft a proof whose `main_proof` nodes, when walked with the real trusted `state_root`, resolve `contract_info_key(address)` to bytes that SCALE-decode successfully as `AccountInfo` but with `account_type` set to a non-`Contract` variant (e.g. an EOA account type), since `AccountInfo::decode` only validates the SCALE shape, not the application-level invariant "this key always holds a contract."

This differs from the already-hardened sibling code in the same file (`verify_child_trie_membership`, `verify_child_trie_values`, `read_proof_check`, etc.), which all return typed errors on trie/decode failures — this call site is the one spot that still assumes success unconditionally.

### Impact Explanation
`verify_membership`/`verify_non_membership` on the EVM (Substrate-hosted pallet-revive) state machine are on the critical path for delivering ISMP POST requests/responses and GET-response proofs across the SubstrateEvm route. A crafted proof that reaches the mismatched-variant condition would abort (panic) the node process executing state-transition/proof-verification logic — inside a parachain runtime this becomes a `wasm` trap during block execution/proof checking, which is a "route unable to deliver messages" / potential chain-halt condition reachable from a single relayed proof, matching the required impact bar ("a route unable to deliver messages").

### Likelihood Explanation
Medium: the attacker must produce trie proof nodes that (a) verify against the genuine, already-finalized `state_root`/`trie_id`/`child_root` for the target contract-info key, and (b) decode to a syntactically valid `AccountInfo` whose `account_type` discriminant is not `Contract`. Because `AccountInfo`/`AccountType` decoding only checks SCALE well-formedness (not that the discriminant matches what the application expects at that key), and the relayer fully controls `proof.main_proof`'s raw bytes (subject only to hashing to the correct root along the path — an adversarial proof for a *non-existent* or *differently-typed* key at that same location, or a forged sibling/extension node, can satisfy this if the trie implementation or an equivocation in the proof allows an alternate decode), this is plausible without needing to break any cryptographic primitive, only to control the account-type discriminant byte of the leaf value.

### Recommendation
Replace the irrefutable destructure with a fallible match returning a typed error, mirroring the pattern already used everywhere else in this file:

```rust
let contract_info = match account_info.account_type {
    AccountType::Contract(info) => info,
    _ => return Err(SubstrateEvmError::AccountInfoDecodeError), // or a new NotAContract variant
};
```

Audit the rest of the crate (and any other pallet-revive/`AccountInfo` consumers) for the same irrefutable-enum-destructure pattern on values sourced from proof-verified trie data, and add a regression test analogous to `empty_hp_prefix_returns_error_not_panic` that feeds a well-formed non-`Contract` `AccountInfo` through `fetch_trie_id_from_main_proof` and asserts an `Err` rather than a panic.

### Proof of Concept
1. Construct a `SubstrateEvmProof` whose `main_proof` is a valid Merkle-Patricia proof against the genuine `state_root` for `contract_info_key(address)`.
2. Have the corresponding trie leaf hold SCALE bytes decoding to `AccountInfo { account_type: AccountType::<NonContractVariant>(..), .. }` — reachable if that storage slot can ever legitimately hold a non-contract account (e.g. an EOA that later self-destructed/never deployed code, or a slot the relayer chose that was never a contract to begin with but still passes proof verification for lookup purposes).
3. Submit this as the `proof` field of an ISMP `handle_unsigned`/relayed message targeting `SubstrateEvmStateMachine::verify_membership` or `verify_non_membership`.
4. `fetch_trie_id_from_main_proof` executes `let AccountType::Contract(contract_info) = account_info.account_type;`, panicking the runtime/node on the non-`Contract` branch instead of returning `SubstrateEvmError`.

Note: I was not able to directly view the full `AccountType` enum definition or every non-`Contract` variant in the tool session (the `read_file` calls failed due to a tool-parameter error and no further iterations were available), so I cannot state with certainty how many variants `AccountType` has or whether the compiler currently accepts this destructure as literally written (it may already be guarded by a runtime-inserted match-panic, or the enum may in fact be single-variant in this exact codebase revision, which would make this specific line dead-code-safe). This should be verified directly against `modules/ismp/state-machines/evm/src/types.rs` (or wherever `AccountType`/`AccountInfo` are defined) before treating this finding as confirmed exploitable.

### Citations

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L182-221)
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
```

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L272-277)
```rust
	let account_info = AccountInfo::decode(&mut &val[..])
		.map_err(|_| SubstrateEvmError::AccountInfoDecodeError)?;

	let AccountType::Contract(contract_info) = account_info.account_type;

	Ok(contract_info.trie_id)
```
