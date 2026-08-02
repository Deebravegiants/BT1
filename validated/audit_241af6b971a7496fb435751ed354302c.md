This confirms the vulnerability. `transaction.votes` is a `SimpleMap<address, bool>` keyed only by address, and votes are never removed from it when an owner is removed via `update_owner_schema`/`remove_owners`/`swap_owners` [1](#0-0) . Vote counting (`num_approvals_and_rejections_internal`) only filters by the *current* owners list at read time rather than deleting stale entries from `votes` [2](#0-1) . The existing test `test_validate_transaction_should_not_consider_removed_owners` only proves the filter works while the address stays out of the owner set [3](#0-2) ; it never exercises the case where that same address is later swapped back in via `swap_owner`/`add_owners` while a transaction created before the removal is still pending, which is exactly the "stale approval survives owner-list change" pattern from the external report.

### Title
Stale Multisig Vote Reactivation on Owner Re-addition — ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
`MultisigTransaction.votes` records approvals/rejections keyed by address and is never purged when an owner is removed. If that same address is later re-added as an owner (via `add_owners`, `swap_owner`/`swap_owners`, or `swap_owners_and_update_signatures_required`) while a transaction created before the removal is still pending, its old vote automatically counts again toward quorum — without the owner casting any new vote under their re-granted authority.

### Finding Description
`vote_transanction` stores votes in `transaction.votes: SimpleMap<address, bool>` [4](#0-3) . `num_approvals_and_rejections_internal` computes quorum by iterating the *current* `owners` vector and looking up each owner's entry in `votes`, effectively "hiding" votes from non-owners rather than deleting them [2](#0-1) . `remove_owners`/`swap_owners` (via `update_owner_schema`) only mutate the `owners` list; they never touch `votes` in any pending `MultisigTransaction`. Consequently, if owner A votes to approve tx #N, is then removed (their vote becomes invisible per the existing regression test), and is subsequently re-added as an owner before tx #N is resolved, `num_approvals_and_rejections_internal` will once again count A's old, stale vote as an active approval — identical in structure to the reported bug where a controller address change leaves a stale grant of authority in place on already-existing state, silently restoring privileged access without a fresh authorization action.

### Impact Explanation
This breaks the core multisig custody invariant that execution requires *current*, freshly-granted approvals from the present owner set. An attacker or compromised former owner who is re-added to the owner set (a routine multisig maintenance operation) can have old votes on stale, still-pending transactions silently reactivate, potentially pushing a malicious or outdated transaction (e.g., a fund transfer, an `add_owners`/`update_signatures_required` payload, or an upgrade of a resource/code object controlled by the multisig) past the quorum threshold without any of the current owners actively re-approving it. Since `MultisigAccount` is commonly used to gate resource-account and code-object control, and to custody APT/fungible assets, this can lead to unauthorized execution of a transaction the current owner set never actually approved — a custody/authority-break impact.

### Likelihood Explanation
Requires a specific sequence: a transaction created and partially approved, then the approving owner removed, then later re-added, all before the transaction is executed or explicitly cleaned up. Owner rotation and pending transactions coexisting is a realistic operational pattern for teams using multisig accounts for treasury/resource-account management, but it depends on the owner-management flow being exercised in this specific order, which is not the most common path — moderate rather than trivial likelihood.

### Recommendation
When `update_owner_schema` removes an owner, purge that owner's entries from `votes` in all pending `MultisigTransaction`s (or alternatively, disallow re-adding a previously-removed-then-rejoining owner's stale votes by clearing votes on any owner-set change, or by re-validating that all counted votes were cast by addresses continuously in the owner set since the vote was cast). At minimum, add explicit handling so that re-adding a previously removed address does not resurrect their old vote on any transaction created prior to their removal.

### Proof of Concept
1. Create a 2-of-3 multisig with owners `{O1, O2, O3}`.
2. `O1` creates transaction #1 (implicit self-approval) — 1/2 approvals.
3. `O2` calls `approve_transaction(O2, multisig, 1)` — 2/2 approvals; `can_be_executed == true`.
4. Multisig-signed governance action calls `remove_owners([O2])` (e.g. because O2's device is suspected compromised) — per existing test, `can_be_executed` becomes `false` since O2's vote is now invisible.
5. Later, multisig-signed action calls `add_owners([O2])` (O2 reinstated, or same address controlled by attacker) with no new vote cast on transaction #1.
6. `can_be_executed(multisig, 1)` re-evaluates to `true` again, because `num_approvals_and_rejections_internal` re-includes O2's stale, never-deleted vote — transaction #1 can now be executed without any current owner having freshly approved it in its current state.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1225-1253)
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

        emit(
            Vote {
                multisig_account,
                owner: owner_addr,
                sequence_number,
                approved,
            }
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
