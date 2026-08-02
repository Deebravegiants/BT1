Confirmed: the `votes` map in `MultisigTransaction` (an `aptos_std::simple_map::SimpleMap<address, bool>`) is keyed purely by owner address and is never cleared when that address is removed from the multisig's owner list. `update_owner_schema` (called by `remove_owners`/`swap_owner`) only mutates `multisig_account_ref_mut.owners` via `vector::swap_remove`; it never touches `multisig_account_resource.transactions[*].votes`. [1](#0-0) [2](#0-1) 

### Title
Stale votes in `MultisigTransaction.votes` are silently reused if a removed owner is re-added before the transaction resolves - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
`vote_transanction` records an owner's approval/rejection in `transaction.votes: SimpleMap<address, bool>`, keyed by the owner's address [3](#0-2) . When an owner is removed via `update_owner_schema`, only the `owners` vector is mutated with `vector::swap_remove`; the `votes` entry for that address inside any still-pending `MultisigTransaction` is left untouched [4](#0-3) . Vote tallying (`num_approvals_and_rejections_internal`) filters votes against the *current* `owners` list, so while the address is not an owner its stale vote is ignored [5](#0-4) . However, if that same address is later re-added as an owner (`add_owners`, `swap_owner`, `swap_owners`) while the transaction is still pending, the old vote automatically becomes "valid" again and counts toward quorum without the owner taking any new action — exactly the same class of bug as the reported `NFTFloorOracle` issue, where removal did not purge nested per-key state (`feederPrice`), so re-adding the key silently revived stale data.

### Impact Explanation
An owner who voted to approve (or reject) a pending transaction, was later removed (e.g., for being compromised, malicious, or simply rotated out), and is subsequently re-added to the multisig (a routine operation, e.g. `swap_owner`/`add_owners` as part of normal owner rotation) will have their old, possibly stale or malicious, vote counted again automatically. This can:
- Push a transaction over the approval quorum (`num_signatures_required`) using a vote cast under a different owner-set context, without the current owner set actually re-confirming it — enabling unauthorized execution of multisig-controlled transactions (which control the multisig's resource account, and any APT/fungible assets/objects it owns).
- Conversely, cause unwanted rejections to count, blocking a legitimate transaction via `execute_rejected_transaction`.
Because a multisig account is a resource account that can hold and transfer APT/fungible assets/objects, corrupted quorum accounting here is a custody-control issue: it can let a transaction execute (moving/transferring assets, changing signer capability usage, etc.) with fewer *genuinely current* approvals than `num_signatures_required` mandates.

### Likelihood Explanation
This requires a specific sequence: an owner votes, is removed, and is re-added while the same transaction (identified by `sequence_number`) is still un-executed. Owner churn (add/remove/swap) is an explicitly supported, non-privileged-in-the-adversarial-sense multisig admin flow that can happen for routine reasons (compromised key rotation, temporary owner changes) while transactions remain pending — the module supports up to `MAX_PENDING_TRANSACTIONS = 20` pending transactions simultaneously, increasing the window during which stale votes can be revived [6](#0-5) . No signature or explicit re-vote is required for the resurrected vote to count.

### Recommendation
On removal of an owner in `update_owner_schema`, iterate all pending transactions (`multisig_account_ref_mut.transactions`, sequence numbers from `last_executed_sequence_number + 1` to `next_sequence_number - 1`) and remove that owner's entry from each transaction's `votes` map, mirroring the recommended fix of purging nested per-key state on removal in the original report.

### Proof of Concept
1. Create a 2-of-3 multisig with owners `A`, `B`, `C`.
2. `A` creates transaction #1 (`create_transaction`).
3. `B` approves transaction #1 (`approve_transaction`) → `votes = {A: true(implicit via creator? no), B: true}`.
4. Multisig removes `B` (`remove_owners([B])`) for unrelated reasons — `can_be_executed` now correctly ignores B's vote since B is not in `owners` (per `num_approvals_and_rejections_internal` filtering by `owners.for_each_ref`) [5](#0-4) .
5. Multisig later re-adds `B` (`add_owners([B])`) as part of routine owner rotation, without B taking any new voting action.
6. `B`'s original approval vote from step 3, still stored in `transaction.votes`, is now counted again by `num_approvals_and_rejections_internal` since `B` is back in `owners` — reaching quorum (2-of-3) potentially without any of the *current* owners having freshly approved, allowing execution of a transaction whose approvals reflect a stale, previously-invalidated ownership context.

Note: I was not able to fully trace every downstream execution-path check (e.g., `can_execute_with_timelock`, full `transaction_execution_cleanup_common`) within the available context, so I cannot rule out an additional safeguard elsewhere that re-validates votes at execution time beyond what's shown in `validate_multisig_transaction`. Based on the code reviewed, no such re-validation of vote freshness relative to owner-membership history exists.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L99-100)
```text
    /// The number of pending transactions has exceeded the maximum allowed.
    const EMAX_PENDING_TRANSACTIONS_EXCEEDED: u64 = 19;
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1235-1253)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1612-1632)
```text
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
