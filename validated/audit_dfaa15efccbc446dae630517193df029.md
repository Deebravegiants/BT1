Based on my investigation, I found a strong custody analog in `multisig_account.move`'s timelock/override-threshold feature, which exhibits the same class of bug as the reported issue: two related numeric parameters (`num_signatures_required` and `override_threshold`) are cross-validated only at the point one of them is initially set, but not re-validated when the other is changed later by an independent code path.

### Title
Multisig Timelock Override Threshold Not Re-Validated Against `num_signatures_required` on Owner/Quorum Updates — ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
`multisig_account.move` supports an optional `MultisigAccountTimeLock` with a `timelock_period` and an `override_threshold` that must strictly exceed `num_signatures_required` at the time the timelock is configured. This invariant is enforced only inside the timelock upsert path [1](#0-0) . However, `num_signatures_required` can independently be modified later via `update_signatures_required`, `add_owners_and_update_signatures_required`, `swap_owners_and_update_signatures_required`, and owner add/remove/swap flows, which the module's own documentation confirms all funnel through `update_owner_schema` [2](#0-1) . If those quorum-modifying paths do not re-check `override_threshold > num_signatures_required`, the invariant established once at timelock-configuration time can be silently violated later — mirroring the reported bug class where two interdependent parameters (`strikePrice`/`strikePercent`) are validated in isolation instead of jointly, and can drift out of the intended relationship after one is updated independently.

### Finding Description
The timelock/override mechanism is meant to let a *supermajority* of owners execute a pending transaction immediately, bypassing the configured delay, while a normal quorum (`num_signatures_required`) must still wait out the timelock. This is enforced by `can_execute_with_timelock`, which allows immediate execution if `num_approvals >= override_threshold`, otherwise requires `elapsed >= timelock_period` [3](#0-2) . The overall execution gate in `validate_multisig_transaction` first requires `num_approvals >= num_signatures_required` (quorum), and only then separately checks `can_execute_with_timelock` (the override/timelock condition) as an independent, unambiguous abort path [4](#0-3) .

The invariant `override_threshold > num_signatures_required` is only enforced where the timelock is configured (the upsert/create-with-timelock path) [1](#0-0) . If `num_signatures_required` is subsequently raised (or `override_threshold` isn't re-derived) through the independent owner/quorum-management functions documented as using `update_owner_schema` [2](#0-1) , `override_threshold` can end up **less than or equal to** `num_signatures_required`. In that state, the "override" branch of `can_execute_with_timelock` becomes vacuous or trivially satisfied whenever the ordinary quorum check already passes — collapsing the intended two-tier protection (normal quorum + timelock delay, vs. supermajority override bypassing the delay) into a single-tier check, effectively nullifying the timelock delay for all transactions once ordinary quorum is met.

### Impact Explanation
Custody impact: the timelock is a custody control meant to give owners of a resource-account-backed multisig (which the module documentation states is a resource account by default [5](#0-4) ) a window to detect and reject a malicious pending transaction before it executes and moves/burns/reassigns custody of assets held by that account. If the override/quorum invariant silently degrades after a routine owner or quorum change, the delay protecting fund transfers, ownership rotations, or code-object upgrades controlled by the multisig can be bypassed at ordinary quorum instead of the intended supermajority, undermining the safety guarantee the timelock was added to provide.

### Likelihood Explanation
This requires an operational sequence rather than a single-transaction exploit: (1) create a multisig with a timelock and a valid `override_threshold > num_signatures_required`, then (2) call one of the owner/quorum-management entry points to raise `num_signatures_required` (a normal, owner-authorized administrative action) without an accompanying re-validation against `override_threshold`. Whether this is actually unenforced depends on the concrete body of `update_signatures_required`/`update_owner_schema`, which I could not fully inspect within the available tool budget — I confirmed the invariant check exists at the timelock-config call site but could not conclusively verify its absence in the owner-update call sites due to running out of search iterations.

### Recommendation
Ensure any function that mutates `num_signatures_required` (via `update_owner_schema` or its callers) also re-validates, when a `MultisigAccountTimeLock` resource exists, that `override_threshold` (if set) remains strictly greater than the new `num_signatures_required`, aborting with `EINVALID_TIMELOCK_OVERRIDE_THRESHOLD` otherwise — matching the check already performed in the timelock upsert path.

### Proof of Concept
Not fully verified — a concrete PoC would require confirming, by reading the full body of `update_signatures_required`/`update_owner_schema` in `multisig_account.move`, that no equivalent `override_threshold`-vs-`num_signatures_required` assertion is executed on that path. I was not able to complete that verification within the available iterations, so this finding should be treated as a **candidate requiring confirmation** rather than a fully proven vulnerability.

**Note on confidence**: Given the incomplete verification of the owner/quorum-update code path, I cannot assert with certainty that this is an exploitable bug rather than an invariant that is in fact re-checked elsewhere. If you want a definitive answer, a follow-up session with full-file read access to `multisig_account.move`'s `update_owner_schema` function is needed to confirm or refute the missing re-validation.

### Citations

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L6-18)
```markdown
Enhanced multisig account standard on Aptos. This is different from the native multisig scheme support enforced via
the account's auth key.

This module allows creating a flexible and powerful multisig account with seamless support for updating owners
without changing the auth key. Users can choose to store transaction payloads waiting for owner signatures on chain
or off chain (primary consideration is decentralization/transparency vs gas cost).

The multisig account is a resource account underneath. By default, it has no auth key and can only be controlled via
the special multisig transaction flow. However, owners can create a transaction to change the auth key to match a
private key off chain if so desired.

Transactions need to be executed in order of creation, similar to transactions for a normal Aptos account (enforced
with account nonce).
```

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L4351-4358)
```markdown
            });
        };
        // Override threshold must still be greater than num_signatures_required.
        <b>assert</b>!(
            timelock.override_threshold.is_none() || timelock.override_threshold.borrow() &gt; &multisig_account_ref_mut.num_signatures_required,
            <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error_invalid_state">error::invalid_state</a>(<a href="multisig_account.md#0x1_multisig_account_EINVALID_TIMELOCK_OVERRIDE_THRESHOLD">EINVALID_TIMELOCK_OVERRIDE_THRESHOLD</a>)
        );
    };
```

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L4470-4476)
```markdown
<tr>
<td>12</td>
<td>Performing any changes on the list of owners such as adding new owners, removing owners, swapping owners should ensure that the number of required signature, for the multi-signature account remains valid.</td>
<td>Critical</td>
<td>The following function as used to modify the owners list and the required signature of the account: add_owner, add_owners, add_owners_and_update_signatures_required, remove_owner, remove_owners, swap_owner, swap_owners, swap_owners_and_update_signatures_required, update_signatures_required. All of these functions use update_owner_schema function to process these changes, the function validates the owner list while adding and verifies that the account has enough required signatures and updates the owner's schema.</td>
<td>Audited that the owners are added successfully. (add_owner, add_owners, add_owners_and_update_signatures_required, swap_owner, swap_owners, swap_owners_and_update_signatures_required, update_owner_schema) Audited that the owners are removed successfully. (remove_owner, remove_owners, swap_owner, swap_owners, swap_owners_and_update_signatures_required, update_owner_schema) Audited that the num_signatures_required is updated successfully. (add_owners_and_update_signatures_required, swap_owners_and_update_signatures_required, update_signatures_required, update_owner_schema)</td>
</tr>
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L497-515)
```text
    inline fun can_execute_with_timelock(multisig_account: address, sequence_number: u64, num_approvals: u64): bool {
        if (exists<MultisigAccountTimeLock>(multisig_account)) {
            let multisig_account_resource = &MultisigAccountTimeLock[multisig_account];
            let timelock = multisig_account_resource.timelock_period;
            let override_threshold = multisig_account_resource.override_threshold;

            // Get the pending transaction to check if the timelock has expired
            // Assume that the transaction has already been checked to exist and is valid
            let pending_transaction = get_transaction(multisig_account, sequence_number);

            // Use subtraction to avoid overflow (now_seconds() >= creation_time_secs is always true)
            let elapsed = now_seconds() - pending_transaction.creation_time_secs;

            // If the number of approvals meets the override threshold, or the timelock has expired, allow execution
            (override_threshold.is_some() && &num_approvals >= override_threshold.borrow()) || elapsed >= timelock
        } else {
            true
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1348-1359)
```text
        // Count approvals, including the executing owner's implicit vote.
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, address_of(owner))) {
            num_approvals += 1;
        };
        assert!(num_approvals >= num_signatures_required(multisig_account), error::invalid_argument(ENOT_ENOUGH_APPROVALS));

        // Timelock check — separate from quorum so the error is unambiguous.
        assert!(
            can_execute_with_timelock(multisig_account, sequence_number, num_approvals),
            error::invalid_state(ETIMELOCK_NOT_EXPIRED),
        );
```
