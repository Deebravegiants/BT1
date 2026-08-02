[1](#0-0)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L2985-3027)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_execute_with_override_bypasses_timelock(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure 1 hour timelock, override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Create transaction and get all 3 owners to approve.
        create_transaction(owner_1, multisig_account, PAYLOAD);
        approve_transaction(owner_2, multisig_account, 1);
        approve_transaction(owner_3, multisig_account, 1);

        // 3 approvals meets override threshold — immediately executable despite timelock.
        assert!(can_be_executed(multisig_account, 1), 0);
        assert!(can_execute(address_of(owner_1), multisig_account, 1), 1);

        // Execute successfully without waiting.
        successful_transaction_execution_cleanup(address_of(owner_1), multisig_account, vector[]);
    }

    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_implicit_vote_counts_toward_override(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure 1 hour timelock, override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Create transaction, 2 explicit approvals (owner_1 auto-approves, owner_2 approves).
        create_transaction(owner_1, multisig_account, PAYLOAD);
        approve_transaction(owner_2, multisig_account, 1);

        // owner_3 hasn't voted. can_execute counts their implicit vote (2+1=3 >= override).
        assert!(can_execute(address_of(owner_3), multisig_account, 1), 0);

        // But can_be_executed doesn't count implicit votes, so it shouldn't pass.
        assert!(!can_be_executed(multisig_account, 1), 1);
    }
```
