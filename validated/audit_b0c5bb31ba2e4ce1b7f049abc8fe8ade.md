### Title
Stale multisig votes are replayed after an owner is removed and re-added, allowing execution of a pending transaction without genuine current-owner consent - ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
`MultisigAccount.transactions` stores a `MultisigTransaction.votes: SimpleMap<address, bool>` keyed by owner address [1](#0-0) . Approval/rejection counts are computed by intersecting this persistent votes map with the *current* owner list via `num_approvals_and_rejections_internal` [2](#0-1) . When owners are changed via `update_owner_schema` (invoked by the multisig account's own governance transactions to add/remove owners), pending transactions' vote entries are never purged or reset [3](#0-2) . This is the same bug class as the reported `replaceGovernance` issue: a vote/consent record tied to an identity is not cleared when the underlying authority configuration changes, and can be silently "replayed" once that configuration is reverted.

### Finding Description
`update_owner_schema` mutates `multisig_account_ref_mut.owners` (appending `new_owners`, `swap_remove`-ing `owners_to_remove`) but never touches `multisig_account_ref_mut.transactions` or any `MultisigTransaction.votes` map [3](#0-2) .

Vote counting (`num_approvals_and_rejections_internal`, used by `can_be_executed`, `can_execute`, and the VM-only `validate_multisig_transaction`) iterates the multisig account's *current* `owners` vector and checks, for each current owner, whether they have an entry in the pending transaction's `votes` map: [2](#0-1) 

The existing regression test `test_validate_transaction_should_not_consider_removed_owners` only proves that a *removed* owner's vote stops counting [4](#0-3) . It does not cover the inverse: if that same owner is later **re-added** while the transaction is still pending, their old vote entry — still sitting untouched in the `votes` `SimpleMap` from before removal — becomes live again and is counted toward quorum without the owner ever re-approving after reinstatement.

Concrete flow:
1. Owners {A, B, C}, `num_signatures_required = 2`. Owner A creates transaction T (auto-vote `true` via `add_transaction`) [5](#0-4) .
2. B and C (via a separate, properly-quorumed multisig transaction) decide to remove A as owner (e.g., suspected key compromise) using `update_owner_schema`'s remove path. T is still pending; A's vote entry in `T.votes` is left in place.
3. Later, B and C decide the compromise concern was unfounded and re-add A as an owner via the `new_owners` path of the same function. No re-validation or purge of `T.votes` occurs.
4. T is still pending (never removed/rejected). Now `num_approvals_and_rejections_internal` again iterates over {A, B, C}, finds A's stale `true` vote in `T.votes`, and counts it — even though A never re-approved T after being reinstated. If a single other owner (say B, who never approved T in the first place, or who approved a different transaction) approves T now, the transaction reaches quorum (A's ghost vote + B's real vote = 2) and can be executed via `validate_multisig_transaction`/`successful_transaction_execution_cleanup`, even though genuine "post-reinstatement" consent from A was never obtained.

This is the on-chain custody analog of the external report: a per-identity vote/consent record that should be invalidated by a configuration change (owner removal) is never reset, so it "revives" and is replayed once the configuration is reverted (owner re-added), enabling execution without proper voting.

### Impact Explanation
Multisig accounts on Aptos are commonly used as resource accounts and code-object/upgrade authorities controlling custody of APT, fungible assets, and object ownership. If a stale vote from a previously-removed-then-reinstated owner can silently count toward quorum, an attacker or compromised/former owner who cast an approval before being removed can have that approval "count again" after being reinstated, letting a minority of *currently* consenting owners push through arbitrary multisig transactions (fund transfers, ownership/authority reassignment, resource-account signer capability usage) that should require full current-owner quorum. This directly threatens theft, unauthorized transfer, or owner-authority reassignment of assets held by the multisig — a custody-grade, mainnet-relevant impact.

### Likelihood Explanation
The precondition (owner temporarily removed and later re-added while a transaction created/approved by that owner is still pending) is a plausible operational pattern (e.g., temporary suspicion of key compromise, key rotation drills, or owner set churn in DAOs/treasuries), and requires no privileged bypass beyond normal multisig owner-management flows that are already exposed as public entry functions (`create_transaction`/`vote_transanction`/owner-management transactions executed through the multisig itself). No special permissions beyond being (at some point) an owner are needed to plant the stale vote.

### Recommendation
When owners are removed in `update_owner_schema`, purge that owner's entries from every pending `MultisigTransaction.votes` map (or, more simply, invalidate/clear the `votes` map entirely for all pending transactions whenever the owner set changes) so that consent must always be re-established against the current owner set. Alternatively, only count votes cast by addresses that were owners continuously since a `last_owner_set_change` timestamp/epoch, tracked per transaction.

### Proof of Concept
Conceptual Move test (extending the existing test module in `multisig_account.move`):
```
create_with_owners(owner_1, vector[owner_2, owner_3], 2, ...);
create_transaction(owner_1, multisig, PAYLOAD);          // owner_1 auto-votes true, seq=1
remove_owners(multisig_signer, vector[owner_1]);         // owner_1's vote entry stays in T.votes
add_owners(multisig_signer, vector[owner_1]);            // owner_1 reinstated, vote NOT reset
// owner_1 never re-approves; owner_2 approves once:
approve_transaction(owner_2, multisig, 1);
assert!(can_be_executed(multisig, 1), 0);                // TRUE: quorum reached via stale vote
```
This is a logical trace based on the code paths cited above; I was not able to execute the Move test suite to confirm compiled behavior, so this should be validated by actually running the test against the framework's test harness.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L180-180)
```text
    /// A transaction to be executed in a multisig account.
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1463-1486)
```text
    inline fun add_transaction(
        creator: address,
        multisig_account: address,
        transaction: MultisigTransaction
    ) {
        if (features::multisig_v2_enhancement_feature_enabled()) {
            assert!(
                available_transaction_queue_capacity(multisig_account) > 0,
                error::invalid_state(EMAX_PENDING_TRANSACTIONS_EXCEEDED)
            );
        };

        let multisig_account_resource = borrow_global_mut<MultisigAccount>(multisig_account);

        // The transaction creator also automatically votes for the transaction.
        transaction.votes.add(creator, true);

        let sequence_number = multisig_account_resource.next_sequence_number;
        multisig_account_resource.next_sequence_number = sequence_number + 1;
        multisig_account_resource.transactions.add(sequence_number, transaction);
        emit(
            CreateTransaction { multisig_account: multisig_account, creator, sequence_number, transaction }
        );
    }
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L2269-2289)
```text
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
