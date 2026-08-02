Confirmed: `update_owner_schema` (aptos-move/framework/aptos-framework/sources/multisig_account.move:1586-1683) only mutates `owners` (append/swap_remove) and never touches `MultisigTransaction.votes` for any pending transaction. Votes are stored in a `SimpleMap<address, bool>` keyed purely by address, and `num_approvals_and_rejections_internal` (lines 1532-1548) counts a vote as valid whenever `simple_map::contains_key(votes, owner)` is true for an address currently in the `owners` vector — with no timestamp, nonce, or "membership epoch" tying the vote to the specific tenure of ownership.### Title
Stale votes on pending multisig transactions can be resurrected when a removed owner is re-added, allowing execution with recycled (non-fresh) approvals - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
`MultisigTransaction.votes` is a `SimpleMap<address, bool>` keyed only by raw address, with no notion of the voter's "ownership epoch." `vote_transanction` writes into this map keyed by `address_of(owner)` [1](#0-0) , and `update_owner_schema` — the sole function used by `add_owners`/`remove_owners`/`swap_owner(s)` — only mutates the `owners` vector; it never inspects or purges `transactions[*].votes` for any pending transaction [2](#0-1) . Vote tallying (`num_approvals_and_rejections_internal`) simply checks whether the *current* owner address happens to have a key in the votes map [3](#0-2) .

### Finding Description
This is the same custody-invariant break as the reported Solidity bug: an approval that is authenticated by an *identity* (address) rather than by a *live authority relationship* is not cleared when that authority is revoked, so if the identity later regains authority, the stale approval silently becomes valid again without any fresh authorization act.

Concretely:
1. Owner `A` calls `approve_transaction`/`reject_transaction` on pending transaction `#N`, which permanently records `votes[A] = approved` inside the `MultisigTransaction` struct stored in the multisig account's `transactions` table [4](#0-3) .
2. The owners later remove `A` via `remove_owner`/`remove_owners` (→ `update_owner_schema`). This removes `A` only from the `owners` vector; `A`'s vote entry in `#N`'s (and any other pending transaction's) `votes` map is left untouched [5](#0-4) . This matches the existing unit test `test_validate_transaction_should_not_consider_removed_owners`, which only proves the vote is *ignored while A is absent from `owners`* — it does not prove the vote is *deleted* [6](#0-5) .
3. If `A` (or, via `swap_owner`/`swap_owners`, the same address is later swapped back in as an owner) is re-added through `add_owners`/`swap_owner`, `update_owner_schema` merely appends the address back into `owners` — again with no interaction with any transaction's `votes` map [7](#0-6) .
4. On the next call to `can_be_executed`/`validate_multisig_transaction`, `num_approvals_and_rejections_internal` iterates the *current* `owners` vector and finds `A` present with `simple_map::contains_key(votes, A) == true`, so `A`'s old, stale vote is counted toward quorum again — with no re-approval action from `A` [3](#0-2) .

The broken invariant: a multisig owner's approval should be tied to the specific tenure/epoch of their ownership; instead it is tied only to the raw address, so revocation-then-reinstatement of an owner address resurrects consent that was never re-affirmed under current owner-set/threshold conditions.

### Impact Explanation
`MultisigAccount` is a resource account model used to custody APT, fungible assets, and object ownership/upgrade authority for many mainnet protocols (this is precisely the "multisig-owned assets, resource accounts... must not leak upgrade, freeze, or transfer authority to unprivileged callers" custody pivot). If a transaction proposal (e.g., a malicious withdrawal, an upgrade to a code object, or a change to the owner/threshold schema itself) is left pending while owner set churns, a resurrected stale vote can let that transaction reach quorum and execute without the intended number of *current, freely-given* approvals — effectively a partial authority bypass on custody-controlling actions. This is high severity because it corrupts the core "k-of-n live consent" custody guarantee the multisig is designed to provide, potentially enabling unauthorized asset transfer or control-plane compromise of the resource account.

### Likelihood Explanation
Likelihood is moderate: it requires (a) a transaction proposal to remain pending across an owner-membership change, and (b) the same address being removed then later reinstated (via `add_owners` or a `swap_owner` in/out/back-in sequence) — both of which are normal, expected multisig-management operations that legitimate owners could unknowingly trigger (e.g., temporarily removing then restoring a signer's key, or rotating custody back to a previous device). No attacker capability beyond being (at some point) a legitimate owner is required; the bug is purely in the framework's failure to purge/version votes, not a privileged-caller assumption.

### Recommendation
Tie each vote to the owner-set version/epoch rather than raw address: either (1) clear all entries in every pending transaction's `votes` map whenever `update_owner_schema` changes the owner list, or (2) add a monotonically increasing `owner_set_version` field to `MultisigAccount`, stamp each vote with the version at cast time, and only count votes in `num_approvals_and_rejections_internal` whose stamped version matches the current version.

### Proof of Concept
Conceptual repro against `multisig_account.move` test harness:
1. `create_with_owners(owner_1, [owner_2, owner_3], 2, ...)`.
2. `create_transaction(owner_1, ms, PAYLOAD)` → auto-approves as `owner_1`.
3. `approve_transaction(owner_2, ms, 1)` → 2 approvals, `can_be_executed == true`.
4. `remove_owner(multisig_signer, owner_2)` → per existing test, `can_be_executed == false` (only 1 valid approval now, from `owner_1`).
5. `add_owner(multisig_signer, owner_2)` (re-add the same address) — no code path clears `transactions[1].votes[owner_2]`.
6. Call `can_be_executed(ms, 1)` again → returns `true`, because `num_approvals_and_rejections_internal` again counts `owner_2`'s stale `votes[owner_2] = true` entry from step 3, even though `owner_2` never re-approved after being re-instated.

This can be verified directly by extending the existing test `test_validate_transaction_should_not_consider_removed_owners` [8](#0-7)  with an `add_owners(multisig_signer, vector[owner_1_addr])` call after the `remove_owners` step and asserting `can_be_executed` flips back to `true` without any new `approve_transaction` call.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1225-1243)
```text
    public entry fun vote_transanction(
        owner: &signer, multisig_account: address, sequence_number: u64, approved: bool) {
        assert_multisig_account_exists(multisig_account);
        let multisig_account_resource = borrow_global_mut<MultisigAccount>(multisig_account);
        assert_is_owner_internal(owner, multisig_account_resource);

        assert!(
            multisig_account_resource.transactions.contains(sequence_number),
            error::not_found(ETRANSACTION_NOT_FOUND),
        );
        let transaction = multisig_account_resource.transactions.borrow_mut(sequence_number);
        let votes = &mut transaction.votes;
        let owner_addr = address_of(owner);

        if (votes.contains_key(&owner_addr)) {
            *votes.borrow_mut(&owner_addr) = approved;
        } else {
            votes.add(owner_addr, approved);
        };
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1532-1548)
```text
    inline fun num_approvals_and_rejections_internal(owners: &vector<address>, transaction: &MultisigTransaction): (u64, u64) {
        let num_approvals = 0;
        let num_rejections = 0;

        let votes = &transaction.votes;
        owners.for_each_ref(|owner| {
            if (simple_map::contains_key(votes, owner)) {
                if (*simple_map::borrow(votes, owner)) {
                    num_approvals += 1;
                } else {
                    num_rejections += 1;
                };
            }
        });

        (num_approvals, num_rejections)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1586-1632)
```text
    /// Add new owners, remove owners to remove, update signatures required.
    fun update_owner_schema(
        multisig_address: address,
        new_owners: vector<address>,
        owners_to_remove: vector<address>,
        optional_new_num_signatures_required: Option<u64>,
    ) {
        assert_multisig_account_exists(multisig_address);
        let multisig_account_ref_mut =
            borrow_global_mut<MultisigAccount>(multisig_address);
        // Verify no overlap between new owners and owners to remove.
        new_owners.for_each_ref(|new_owner_ref| {
            assert!(
                !vector::contains(&owners_to_remove, new_owner_ref),
                error::invalid_argument(EOWNERS_TO_REMOVE_NEW_OWNERS_OVERLAP)
            )
        });
        // If new owners provided, try to add them and emit an event.
        if (new_owners.length() > 0) {
            multisig_account_ref_mut.owners.append(new_owners);
            validate_owners(
                &multisig_account_ref_mut.owners,
                multisig_address
            );
            emit(AddOwners { multisig_account: multisig_address, owners_added: new_owners });
        };
        // If owners to remove provided, try to remove them.
        if (owners_to_remove.length() > 0) {
            let owners_ref_mut = &mut multisig_account_ref_mut.owners;
            let owners_removed = vector[];
            owners_to_remove.for_each_ref(|owner_to_remove_ref| {
                let (found, index) =
                    vector::index_of(owners_ref_mut, owner_to_remove_ref);
                if (found) {
                    vector::push_back(
                        &mut owners_removed,
                        vector::swap_remove(owners_ref_mut, index)
                    );
                }
            });
            // Only emit event if owner(s) actually removed.
            if (owners_removed.length() > 0) {
                emit(
                    RemoveOwners { multisig_account: multisig_address, owners_removed }
                );
            }
        };
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L2268-2289)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_validate_transaction_should_not_consider_removed_owners(
        owner_1: &signer, owner_2: &signer, owner_3: & signer) {
        setup();
        let owner_1_addr = address_of(owner_1);
        let owner_2_addr = address_of(owner_2);
        let owner_3_addr = address_of(owner_3);
        create_account(owner_1_addr);
        let multisig_account = get_next_multisig_account_address(owner_1_addr);
        create_with_owners(owner_1, vector[owner_2_addr, owner_3_addr], 2, vector[], vector[]);

        // Owner 1 and 2 approved but then owner 1 got removed.
        create_transaction(owner_1, multisig_account, PAYLOAD);
        approve_transaction(owner_2, multisig_account, 1);
        // Before owner 1 is removed, the transaction technically has sufficient approvals.
        assert!(can_be_executed(multisig_account, 1), 0);
        let multisig_signer = &create_signer(multisig_account);
        remove_owners(multisig_signer, vector[owner_1_addr]);
        // Now that owner 1 is removed, their approval should be invalidated and the transaction no longer
        // has enough approvals to be executed.
        assert!(!can_be_executed(multisig_account, 1), 1);
    }
```
