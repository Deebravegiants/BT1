### Title
Unchecked runtime account-type projection in `fetch_trie_id_from_main_proof` causes type confusion / panic on attacker-influenced state proof - (File: `modules/ismp/state-machines/evm/src/substrate_evm.rs`)

### Summary
The Lean 4 CVE is a type-confusion bug where the kernel accepted a `.proj C 0` projection on a value whose actual runtime type did not match the structure `C` named in the projection, because a nested-inductive check was skipped. The analogous pattern in Hyperbridge's `SubstrateEvmStateMachine::verify_state_proof` path is `fetch_trie_id_from_main_proof`, which decodes an `AccountInfo` from a relayer-supplied Merkle proof and then **irrefutably destructures** its `account_type` field as `AccountType::Contract(..)` without checking that the decoded variant actually is `Contract`:

```rust
let account_info = AccountInfo::decode(&mut &val[..])
    .map_err(|_| SubstrateEvmError::AccountInfoDecodeError)?;
let AccountType::Contract(contract_info) = account_info.account_type;
Ok(contract_info.trie_id)
``` [1](#0-0) 

### Finding Description
`fetch_trie_id_from_main_proof` is reached from `SubstrateEvmStateMachine::verify_state_proof` and `verify_non_membership`, both of which are invoked from `pallet-ismp`'s `handle_unsigned` extrinsic (an unsigned, unprivileged, relayer-submitted transaction) when processing a GET response or a request non-membership proof against a `substrate-evm` (pallet-revive) counterparty:

```rust
let trie_id = fetch_trie_id_from_main_proof::<H>(
    &proof.main_proof,
    state_root,
    &contract_info_key,
)?;
``` [2](#0-1) 

The `main_proof` is a raw, attacker-controlled set of trie nodes decoded from the relayer's `SubstrateEvmProof` (`Decode::decode(&mut &proof.proof[..])`, no further validation of node contents beyond trie-inclusion). Once trie inclusion against the trusted `state_root` is checked, the leaf bytes are SCALE-decoded into an `AccountInfo` whose `account_type` field is an enum (at minimum `Contract` and presumably an EOA/other variant, mirroring pallet-revive's `AccountType`). The code assumes — without checking — that the decoded variant is always `Contract` and irrefutably destructures it:

```rust
let AccountType::Contract(contract_info) = account_info.account_type;
```

This is precisely the class of bug in the Lean report: a projection (`.proj Contract 0` — "read field 0 assuming this value has type/shape `Contract`") is applied to a value without first verifying its tag/type matches. In Lean the kernel is supposed to enforce this and a bug let it slip through; here, Rust's own type system would normally force an exhaustive match, but the code sidesteps that guarantee with an irrefutable `let` pattern that only compiles because `AccountType` was treated as if it had one inhabited variant reachable via this leaf — any other pattern arm is unreachable code the compiler doesn't insert a runtime check for beyond a `match` failure, i.e. this construct **panics** if the enum has more than one variant and the runtime value present in the proof is not `Contract`.

Because the value being projected/matched comes directly from an untrusted, attacker-supplied Merkle-proof leaf (subject only to a hash-inclusion check, not to any semantic validation that it is the type the code expects), a relayer can craft a `main_proof` whose leaf at the `contract_info_key` slot decodes to a valid, non-`Contract` `AccountType` variant (e.g., an EOA account entry, which legitimately exists in the same storage map keyed by address) that is nonetheless included under the real, trusted `state_root`. This drives `fetch_trie_id_from_main_proof` — and transitively the entire message-verification handler — into the mismatched-projection panic, the same "read past what the type checker guaranteed" failure mode as the Lean CVE, except here the runtime crashes the node executing `handle_unsigned` for every relayer/validator that processes the proof, rather than yielding a false proof.

### Impact Explanation
This function sits directly on the reachable path from a single, unsigned, unauthenticated extrinsic (`pallet_ismp::Pallet::handle_unsigned`) that any relayer can submit with a real state proof against a real, trusted `state_root` for a `substrate-evm` counterparty. Triggering the mismatched variant produces a runtime panic during state-proof verification of an ISMP message, which is executed inside `handle_unsigned`'s dispatch logic — since this runs inside block execution (unsigned extrinsics still execute on-chain once accepted by the pool), a panic here can halt/crash the validating node, denying message delivery for the `substrate-evm` route entirely (a "route unable to deliver messages" condition) or, depending on how the runtime panic handler is configured, cause non-deterministic node behavior across validators. It does not appear to lead to fund theft directly, but it satisfies the required category of "a route unable to deliver messages."

### Likelihood Explanation
Reaching the vulnerable projection requires only: (1) a `substrate-evm` consensus client configured for a live `state_id`, (2) an attacker able to submit a `handle_unsigned` extrinsic (permissionless, by design), and (3) constructing a `main_proof` whose leaf at the `contract_info_key` for the queried address decodes to a legitimate but non-`Contract` `AccountType` variant that is genuinely included in the real (trusted) `state_root` — e.g., an address in the destination chain's `Revive::AccountInfoOf` map that is an EOA rather than a contract. Since account info for arbitrary EOA addresses commonly exists in the trie already, no forged root is even needed; the attacker only needs to choose keys/queries whose destination-chain storage happens to encode a non-`Contract` account, or await/target such state naturally. This makes the trigger condition plausible without any privileged access, though it is contingent on the exact shape of `AccountType` (unconfirmed from available context whether it has variants beyond `Contract`) — I could not fully verify the enum definition's variant list within the available tool budget, so likelihood is assessed as credible-but-not-fully-confirmed.

### Recommendation
Replace the irrefutable `let AccountType::Contract(contract_info) = account_info.account_type;` with an explicit, fallible match that returns a typed `SubstrateEvmError` (e.g., `SubstrateEvmError::AccountIsNotContract`) for any non-`Contract` variant, mirroring how every other decode step in this file already returns a `Result` instead of panicking. This converts an attacker-reachable panic/type-confusion into a normal proof-rejection error path consistent with the rest of `verify_state_proof`.

### Proof of Concept
1. Configure a `SubstrateEvmStateMachine` client for a live pallet-revive-based `state_id`.
2. As an unprivileged relayer, submit `pallet_ismp::handle_unsigned` with a `RequestMessage`/`ResponseMessage`/timeout message whose `keys` target a 52-byte contract-storage key for an address `A`.
3. Supply a `SubstrateEvmProof.main_proof` containing genuine trie nodes (inclusion-valid against the real, current `state_root`) such that the `Revive::AccountInfoOf` leaf for address `A` decodes to a non-`Contract` `AccountType` variant (e.g. because `A` is an externally-owned account rather than a deployed contract).
4. `fetch_trie_id_from_main_proof` decodes this leaf successfully (trie inclusion passes, SCALE decode of `AccountInfo` succeeds) and then executes `let AccountType::Contract(contract_info) = account_info.account_type;`, which panics because the pattern is not satisfied by the actual (non-`Contract`) variant, aborting the extrinsic's execution mid-block.

Note: I was not able to retrieve and confirm the full definition of the `AccountType` enum (specifically whether it has additional non-`Contract` variants) before the session ended; this finding's severity is contingent on that enum being non-trivial (more than one variant). If `AccountType` truly only has a single `Contract` variant, this specific instance would not be exploitable and the analog would not hold — this should be verified directly in the repository.

### Citations

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L213-218)
```rust
			let contract_info_key = contract_info_key(address);
			let trie_id = fetch_trie_id_from_main_proof::<H>(
				&proof.main_proof,
				state_root,
				&contract_info_key,
			)?;
```

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L272-277)
```rust
	let account_info = AccountInfo::decode(&mut &val[..])
		.map_err(|_| SubstrateEvmError::AccountInfoDecodeError)?;

	let AccountType::Contract(contract_info) = account_info.account_type;

	Ok(contract_info.trie_id)
```
