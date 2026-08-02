## Custody Analog Found

### Title
Multisig votes can be freely flipped after quorum + timelock expiry, letting owners retroactively reject an already-executable transaction and gas-grief/DoS the executor - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The Llama disapproval bug reduces to one custody invariant: once an action has satisfied every requirement to be executed (enough approvals + minimum time elapsed), an adversarial voter should not be able to retroactively flip the action into a "rejected"/blocked state to grief the eventual executor. Aptos's `multisig_account` module (recently extended with a `MultisigAccountTimeLock` feature) has the exact same gap: `vote_transanction` lets any owner overwrite their vote (approve ⇄ reject) at any time, with no restriction once the transaction has already reached quorum and its timelock has expired.

### Finding Description
`vote_transanction` unconditionally overwrites an owner's stored vote regardless of the transaction's current state: [1](#0-0) 

`can_execute_with_timelock` only gates whether a transaction can be *executed early* (before `timelock_period` elapses, unless an `override_threshold` of approvals is met); it places no restriction on *rejection* voting: [2](#0-1) 

The project's own test suite documents this explicitly: rejection voting is immune to the timelock in either direction, i.e. it can happen at any time before or after the transaction becomes executable: [3](#0-2) 

Because `num_approvals_and_rejections` is derived live from the mutable `votes` map every time `can_be_executed`/`can_execute`/`can_be_rejected` are evaluated, an owner who already approved a transaction (contributing to quorum) can call `reject_transaction` to flip their own vote to `false` at the last moment — even after the transaction has passed its timelock and become fully executable. If enough owners who previously approved flip to reject (reaching `num_signatures_required` rejections), `can_be_rejected` becomes true and `execute_rejected_transaction` will remove the transaction from the queue: [4](#0-3) 

This is the identical shape of the Llama finding: the "minExecutionTime"-equivalent gate (`can_execute_with_timelock`) only protects *early* execution, but the state that determines "is this final and safe to execute" (quorum status) is not frozen once that gate opens. An honest owner who observes `can_be_executed(...) == true` and submits `execute_*` can be front-run by owners who flip their votes to reject, causing the honest executor's transaction to fail (their sequence number no longer matches `last_resolved_sequence_number + 1`, or the payload lookup fails) after the transaction has been removed — wasting the honest executor's gas and reversing a transaction that had already legitimately cleared both quorum and timelock.

### Impact Explanation
This module underlies Aptos's native enhanced multisig accounts, which are resource accounts that can hold and control APT, fungible assets, and object ownership. The multisig's core custody guarantee is: "once k-of-n owners approve and the timelock (if configured) has elapsed, the transaction *will* execute as intended." This finding breaks that guarantee — a minority coalition that once approved (or any set of owners reaching the rejection threshold) can retroactively veto a transaction after it has become executable, at the exact moment execution is attempted. Beyond simple gas griefing of the caller, this undermines the entire purpose of the timelock feature: users/monitors are meant to be able to trust that after the timelock window passes, the approved payload (e.g., a fund transfer, ownership transfer, or upgrade) is guaranteed executable; instead it remains cancellable indefinitely, which can be used to permanently block time-sensitive custody operations (e.g., emergency fund recovery or freeze-lift transactions) that depend on deterministic execution once quorum+timelock are satisfied.

### Likelihood Explanation
Any account owner (not a privileged "force" role) can call `reject_transaction`/`vote_transanction` at will, with no state check preventing votes from being changed after quorum or after timelock expiry. Exploitation requires only that the number of owners willing to flip their vote (or newly vote reject) reach `num_signatures_required` — the same threshold already needed for approval — making this trivially reachable by any coalition capable of approving the transaction in the first place, including within the same multisig's honest owner set turning malicious after initial approval, or an owner strategically delaying their explicit vote and reneging once execution is imminent.

### Recommendation
Once a transaction satisfies `can_be_executed` (quorum reached and, if configured, `can_execute_with_timelock` returns true), disallow further rejection votes from owners who already contributed to quorum, or more simply, freeze the vote tally for a transaction once it becomes executable (mirroring the C4 recommendation: `require(!can_be_executed(...))` inside `vote_transanction` for reject votes, i.e., disallow casting a rejection once quorum + timelock conditions are already met, unless the vote is a first-time rejection that could not have contributed to prior quorum).

### Proof of Concept
1. Create a 2-of-3 multisig account with a timelock via `create_with_owners_and_timelock`/`upsert_timelock` (`timelock_period = T`, no override or override > 2).
2. `owner_1` calls `create_transaction` (implicit approve). `owner_2` calls `approve_transaction` — quorum (2 approvals) reached.
3. Advance time by `T`. Now `can_be_executed(multisig, seq) == true` per `aptos-move/framework/aptos-framework/sources/multisig_account.move:471-479`.
4. Before any owner submits the execute transaction, `owner_1` calls `reject_transaction(owner_1, multisig, seq)` (flipping their earlier approve to reject) and `owner_3` calls `reject_transaction(owner_3, multisig, seq)`. Now `num_rejections = 2 == num_signatures_required`, so `can_be_rejected(...) == true` (`multisig_account.move:517-524`).
5. `owner_1` (or anyone) calls `execute_rejected_transaction`, which calls `remove_executed_transaction` and removes the transaction (`multisig_account.move:1273-1305`).
6. `owner_2`'s pending/in-flight `execute` call (submitted based on step 3's `can_be_executed == true`) now fails because the sequence number/transaction no longer exists — griefing `owner_2`'s gas and reversing a fully quorate, timelock-cleared transaction.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L495-524)
```text
    /// Return true if the transaction with given transaction id can be executed immediately, or it has to wait
    /// for the timelock to expire.
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

    #[view]
    /// Return true if the transaction with given transaction id can be officially rejected.
    public fun can_be_rejected(multisig_account: address, sequence_number: u64): bool {
        assert_valid_sequence_number(multisig_account, sequence_number);
        let (_, num_rejections) = num_approvals_and_rejections(multisig_account, sequence_number);
        sequence_number == last_resolved_sequence_number(multisig_account) + 1 &&
            num_rejections >= num_signatures_required(multisig_account)
    }
```

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1273-1305)
```text
    /// Remove the next transaction if it has sufficient owner rejections.
    public entry fun execute_rejected_transaction(
        owner: &signer,
        multisig_account: address,
    ) {
        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);

        let sequence_number = last_resolved_sequence_number(multisig_account) + 1;
        let owner_addr = address_of(owner);
        if (features::multisig_v2_enhancement_feature_enabled()) {
            // Implicitly vote for rejection if the owner has not voted for rejection yet.
            if (!has_voted_for_rejection(multisig_account, sequence_number, owner_addr)) {
                reject_transaction(owner, multisig_account, sequence_number);
            }
        };

        let multisig_account_resource = borrow_global_mut<MultisigAccount>(multisig_account);
        let (_, num_rejections) = remove_executed_transaction(multisig_account_resource);
        assert!(
            num_rejections >= multisig_account_resource.num_signatures_required,
            error::invalid_state(ENOT_ENOUGH_REJECTIONS),
        );

        emit(
            ExecuteRejectedTransaction {
                multisig_account,
                sequence_number,
                num_rejections,
                executor: address_of(owner),
            }
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3044-3061)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_timelock_does_not_block_rejection(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure 1 hour timelock.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Create transaction, then reject it.
        create_transaction(owner_1, multisig_account, PAYLOAD);
        reject_transaction(owner_1, multisig_account, 1);
        reject_transaction(owner_2, multisig_account, 1);

        // Rejection is not subject to the timelock — can reject immediately.
        assert!(can_be_rejected(multisig_account, 1), 0);
        execute_rejected_transaction(owner_1, multisig_account);
```
