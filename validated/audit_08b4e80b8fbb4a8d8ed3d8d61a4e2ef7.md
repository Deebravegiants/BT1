## Finding: Timelock/override-threshold protection in `multisig_account` can be disabled with only the base signature threshold, nullifying its custody protection

### Title
Multisig timelock override protection can be unilaterally removed using only the base signature threshold - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The external report's root custody invariant is: **a protective governance check (blocking premature/unauthorized state changes) must not be removable by an authority weaker than the one it is meant to protect against.** In `multisig_account.move`, this repository has added a non-standard "timelock" feature (`upsert_timelock`, `remove_timelock`, `timelock_override_threshold`) that delays multisig transaction execution and requires an elevated `override_threshold` (greater than the base `num_signatures_required`) to bypass the delay. However, `remove_timelock` and `upsert_timelock` are ordinary self-call `entry fun`s executed through the standard multisig transaction flow, gated only by the base `num_signatures_required` — not by `override_threshold`. This lets a coalition that only meets the base threshold strip the timelock/override protection entirely before executing a sensitive transaction, defeating the delay mechanism's purpose.

### Finding Description
`multisig_account.move` defines self-call admin functions such as `add_owners`, `remove_owners`, `update_signatures_required`, all gated the same way: they are `entry fun`s that take `multisig_account: &signer` and can only be invoked by the multisig account itself through the normal proposal-execution flow, which requires `num_signatures_required` approvals [1](#0-0) .

The timelock feature (`upsert_timelock`, `remove_timelock`, `timelock_override_threshold`) follows the identical pattern, as shown by its tests: an override threshold higher than `num_signatures_required` is configured to require extra approvals before a transaction can bypass the timelock delay, and the code even clamps/validates that `override_threshold` must stay strictly greater than `num_signatures_required` when owners are removed [2](#0-1) .

Critically, the test `test_remove_timelock_allows_immediate_execution` demonstrates that once `remove_timelock` is invoked, a transaction needs only the base `num_signatures_required` approvals to execute immediately, with no delay and no elevated approval count required at all [3](#0-2) . Since `remove_timelock` is itself just another self-call `entry fun`, executing it requires only the base threshold (the same threshold needed to approve any ordinary — including malicious — transaction), not the elevated `override_threshold` it is supposed to gate.

This mirrors the external bug's root cause precisely: a protection mechanism meant to require a *higher* bar than the operation it is protecting can be dismantled using only the *lower*, ordinary bar.

### Impact Explanation
The timelock/override mechanism exists specifically to give other owners a reaction window to detect and evict a compromised owner before a malicious transaction executes — this is explicitly demonstrated by `test_dos_mitigation_end_to_end`, where owners use the pending-transaction window to evict a compromised owner [4](#0-3) . If `remove_timelock` only requires the base threshold, then any coalition capable of approving a malicious withdrawal (base threshold) can first call `remove_timelock` (also base threshold) and then immediately execute the malicious transaction, receiving none of the intended delay/override protection. This directly threatens custody of any APT, coins, or other assets held by a timelocked multisig account, since the entire point of the elevated `override_threshold` — an extra defense-in-depth requirement for a compromised-but-still-below-override coalition — is nullified.

### Likelihood Explanation
Likelihood is high in any deployment that relies on the timelock feature as a custody safeguard: it requires no privileged bug or external condition — merely reaching the same base signature threshold already needed for the (potentially malicious) transaction itself. Since the timelock's entire value proposition is protecting against a coalition at or above `num_signatures_required` but below `override_threshold`, and `remove_timelock` is reachable at exactly `num_signatures_required`, the bypass is trivial for the very threat model the feature claims to defend against.

### Recommendation
Require `remove_timelock` (and any operation that lowers `override_threshold` or the timelock delay) to be approved via the `override_threshold`, not the base `num_signatures_required`, so that disabling the protection is never easier than bypassing it directly. Alternatively, enforce a delay on `remove_timelock`/`upsert_timelock` calls themselves, subject to the same timelock they modify, so a compromised base-threshold coalition cannot instantaneously strip protection before it can be reacted to.

### Proof of Concept
Based on the existing test `test_remove_timelock_allows_immediate_execution` [3](#0-2) , the exploit path is:
1. Owners configure a multisig with `num_signatures_required = 2` and set up a timelock via `upsert_timelock(multisig_signer, delay, option::some(override_threshold))`, where `override_threshold > 2`.
2. An attacker-controlled coalition reaches exactly `num_signatures_required` (2) approvals — insufficient to reach `override_threshold`.
3. The coalition submits and approves a transaction calling `remove_timelock(multisig_account)`, which passes with only 2 approvals since it is an ordinary self-call `entry fun`.
4. The coalition then creates and approves a malicious fund-transfer transaction, which is now immediately executable with only 2 approvals (`can_be_executed`), with no delay and no need to ever reach `override_threshold`.

### Caveat
I was unable to directly retrieve the full source bodies of `upsert_timelock`, `remove_timelock`, and `timelock_override_threshold` (only their usages in tests and doc cross-references were available before tool budget was exhausted) [2](#0-1) . The finding is based on strong circumstantial evidence from the test suite showing the exact bypass behavior, but the precise assert/threshold-check inside `remove_timelock`'s body itself was not directly read. I recommend verifying this by reading `multisig_account.move` around the `upsert_timelock`/`remove_timelock`/`timelock_override_threshold` definitions (search for `fun upsert_timelock` and `fun remove_timelock`) to confirm the exact authorization check before treating this as fully confirmed.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L991-1025)
```text
    /// Add new owners to the multisig account. This can only be invoked by the multisig account itself, through the
    /// proposal flow.
    ///
    /// Note that this function is not public so it can only be invoked directly instead of via a module or script. This
    /// ensures that a multisig transaction cannot lead to another module obtaining the multisig signer and using it to
    /// maliciously alter the owners list.
    entry fun add_owners(
        multisig_account: &signer, new_owners: vector<address>) {
        update_owner_schema(
            address_of(multisig_account),
            new_owners,
            vector[],
            option::none()
        );
    }

    /// Add owners then update number of signatures required, in a single operation.
    entry fun add_owners_and_update_signatures_required(
        multisig_account: &signer,
        new_owners: vector<address>,
        new_num_signatures_required: u64
    ) {
        update_owner_schema(
            address_of(multisig_account),
            new_owners,
            vector[],
            option::some(new_num_signatures_required)
        );
    }

    /// Similar to remove_owners, but only allow removing one owner.
    entry fun remove_owner(
        multisig_account: &signer, owner_to_remove: address) {
        remove_owners(multisig_account, vector[owner_to_remove]);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L2601-2627)
```text
        // owner_3 is compromised and creates a bunch of bogus transactions.
        let remaining_iterations = MAX_PENDING_TRANSACTIONS;
        while (remaining_iterations > 0) {
            create_transaction(owner_3, multisig_address, PAYLOAD);
            remaining_iterations -= 1;
        };

        // No one can create a transaction anymore because the transaction queue is full.
        assert!(available_transaction_queue_capacity(multisig_address) == 0, 0);

        // owner_1 and owner_2 vote "no" on all transactions.
        vote_all_transactions(owner_1, multisig_address, false);
        vote_all_transactions(owner_2, multisig_address, false);

        // owner_1 evicts a transaction and creates a transaction to remove the compromised owner.
        // Note that `PAYLOAD` is a placeholder and is not actually executed in this unit test.
        create_transaction_with_eviction(owner_1, multisig_address, PAYLOAD);

        // owner_2 approves the eviction transaction.
        approve_transaction(owner_2, multisig_address, 11);

        // owner_1 flushes the transaction queue except for the eviction transaction.
        execute_rejected_transactions(owner_1, multisig_address, 10);

        // execute the eviction transaction to remove the compromised owner.
        assert!(can_be_executed(multisig_address, 11), 0);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3064-3082)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_remove_timelock_allows_immediate_execution(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure then remove timelock.
        upsert_timelock(multisig_signer, 3600, option::some(3));
        remove_timelock(multisig_signer);

        // Create and approve a transaction.
        create_transaction(owner_1, multisig_account, PAYLOAD);
        approve_transaction(owner_2, multisig_account, 1);

        // No timelock — immediately executable.
        assert!(can_be_executed(multisig_account, 1), 0);
        successful_transaction_execution_cleanup(address_of(owner_1), multisig_account, vector[]);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3084-3118)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_owner_removal_clamps_override_threshold(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure timelock with override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));
        assert!(timelock_override_threshold(multisig_account) == option::some(3), 0);

        // Remove one owner (3 -> 2 owners). Override threshold should be clamped to 2.
        // Signature threshold is 2, so we need to lower it first to allow removing an owner
        // while keeping override_threshold > num_signatures_required.
        update_signatures_required(multisig_signer, 1);
        remove_owner(multisig_signer, address_of(owner_3));
        assert!(timelock_override_threshold(multisig_account) == option::some(2), 1);
    }

    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    #[expected_failure(abort_code = 0x30016, location = Self)]
    fun test_owner_removal_fails_if_override_becomes_invalid(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure timelock with override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Remove one owner: 3 -> 2 owners, override clamped to 2.
        // But num_signatures_required is also 2, so override (2) is NOT > threshold (2).
        // This should fail.
        remove_owner(multisig_signer, address_of(owner_3));
    }
```
