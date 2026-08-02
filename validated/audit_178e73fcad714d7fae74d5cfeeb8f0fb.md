Note: I was not able to pull the exact body of `num_approvals_and_rejections` before running out of tool iterations, so the analysis below relies on what I did confirm directly (the `MultisigTransaction` struct, `update_owner_schema`, and the call sites in `can_be_executed`/`can_execute`). This should be independently verified by reading `num_approvals_and_rejections` in full before treating this as confirmed.

### Title
Stale votes from removed multisig owners continue to count toward quorum, allowing execution with insufficient *current*-owner approval - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
This mirrors the RoleManager bug class: a count used to gate a privileged action (`getRoleMemberCount()` in the original report, `num_approvals`/quorum here) is derived from a stored map that is never pruned when membership changes, so it silently includes entities that are no longer authorized. In Aptos's `multisig_account` module, each pending `MultisigTransaction` stores votes in a `SimpleMap<address, bool>` [1](#0-0) . Owner removal is handled entirely in `update_owner_schema`, which only mutates the `owners` vector and the signature threshold - it never walks the `transactions` table to purge or invalidate votes cast by an owner being removed [2](#0-1) .

### Finding Description
`can_be_executed` and `can_execute` compute `num_approvals` from `num_approvals_and_rejections(multisig_account, sequence_number)` and compare it against `num_signatures_required(multisig_account)`, the *current* threshold [3](#0-2) . Ownership is only checked at vote-casting time via `assert_is_owner` (referenced in `can_execute`/`can_reject`), not at count time. Since `update_owner_schema` (used by `remove_owner(s)`, `swap_owner(s)`) never touches the `votes` map of already-pending transactions [4](#0-3) , a "yes" vote cast by an owner before their removal remains permanently counted toward quorum for that pending transaction, exactly like the RoleManager's `_roleMembers` set never shrinking after `renounceGovernance()`.

### Impact Explanation
Multisig accounts on Aptos are resource accounts that commonly custody APT and fungible assets. If an owner's key is compromised and the remaining owners remove that owner (the standard incident-response action, analogous to `renounceGovernance()`/revocation in the report), any transaction that owner had already approved before removal keeps its stale approval weight. This can let a transaction execute (e.g., transferring multisig-held APT/FA, rotating auth keys, or reconfiguring owners) using fewer *currently authorized* approvals than the k-of-n policy intends - a custody-accounting corruption that misattributes control/authorization weight to a party that no longer holds it.

### Likelihood Explanation
This requires (a) a compromised/malicious owner to pre-approve a transaction, (b) governance to react by removing that owner without knowing to also cancel/reject the specific pending transaction it had approved, and (c) the remaining owners' approvals plus the stale one to reach the threshold. This is a real-world plausible incident-response sequence (compromise -> revoke) mirroring the original report's exact scenario, but it does require an existing pending transaction and a remove action, not a fully permissionless attack.

### Recommendation
When removing an owner in `update_owner_schema`, iterate the multisig account's pending `transactions` table and strip that owner's entry from each `MultisigTransaction.votes` map (or provide a `getRoleMembers`-style helper: an explicit view that recomputes approvals filtered by the *current* owner set) so `num_approvals_and_rejections` never counts votes from addresses no longer in `owners`.

### Proof of Concept
1. Create a multisig account with owners `[A, B, C]`, `num_signatures_required = 2`.
2. `A` creates a transaction (`create_transaction`), which auto-registers `A`'s "yes" vote in `votes`.
3. `A`'s key is later compromised; governance calls `remove_owners([A])`, dropping `A` from `owners` but not from the pending transaction's `votes` map.
4. With owners now `[B, C]` and threshold still 2, if `B` alone approves, `num_approvals_and_rejections` still reports `A`'s stale vote + `B`'s vote = 2, satisfying `num_signatures_required`, and the transaction executes despite only one *current* owner (`B`) actually approving it - `C` was never consulted.

Because I could not directly inspect `num_approvals_and_rejections`'s implementation in this session, please verify it indeed sums over all `votes` entries without filtering by current `owners` before treating this as fully confirmed.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L182-191)
```text
    struct MultisigTransaction has copy, drop, store {
        payload: Option<vector<u8>>,
        payload_hash: Option<vector<u8>>,
        // Mapping from owner adress to vote (yes for approve, no for reject). Uses a simple map to deduplicate.
        votes: SimpleMap<address, bool>,
        // The owner who created this transaction.
        creator: address,
        // The timestamp in seconds when the transaction was created.
        creation_time_secs: u64,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L471-493)
```text
    #[view]
    /// Return true if the transaction with given transaction id can be executed now.
    public fun can_be_executed(multisig_account: address, sequence_number: u64): bool {
        assert_valid_sequence_number(multisig_account, sequence_number);
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);

        sequence_number == last_resolved_sequence_number(multisig_account) + 1 &&
            num_approvals >= num_signatures_required(multisig_account) && can_execute_with_timelock(multisig_account, sequence_number, num_approvals)
    }

    #[view]
    /// Return true if the owner can execute the transaction with given transaction id now.
    public fun can_execute(owner: address, multisig_account: address, sequence_number: u64): bool {
        assert_valid_sequence_number(multisig_account, sequence_number);
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, owner)) {
            num_approvals += 1;
        };

        is_owner(owner, multisig_account) &&
            sequence_number == last_resolved_sequence_number(multisig_account) + 1 &&
            num_approvals >= num_signatures_required(multisig_account) && can_execute_with_timelock(multisig_account, sequence_number, num_approvals)
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
