This confirms the analysis. The nonce/fee-payer coupling is fully independent of `cpi.rs`'s CPI-exit account synchronization.

### Title
No vulnerability found: nonce-advance/fee-charge coupling is decided by `RollbackAccounts`, not by CPI-exit ordering in `cpi.rs`

### Summary
The premise conflates two unrelated subsystems: `cpi_common`'s post-`process_instruction` account synchronization (`update_caller_account` in `program-runtime/src/cpi.rs`) only mirrors the callee's on-chain account state back into the *caller's VM-visible* `AccountInfo` buffers for use within the same instruction; it has no bearing on what gets committed to the bank. The actual coupling between nonce-advance and fee-debit is established entirely in `svm/src/transaction_processor.rs` and `svm/src/rollback_accounts.rs`, computed *before* execution even starts and applied atomically regardless of success or failure.

### Finding Description
`cpi_common` (<cite repo="Tylerpinwa/agave--029" path="program-runtime/src/cpi.rs" start="839="843" /> then <cite repo="Tylerpinwa/agave--029" path="program-runtime/src/cpi.rs" start="848="865" />) only updates the caller's VM memory-mapped `AccountInfo` view after `process_instruction` returns—this affects what the *calling program* can subsequently read/write via its own `AccountInfo` struct, not whether the transaction is committed or what account state accounts_db stores.

The actual decision of what gets persisted for nonce/fee-payer is made in `TransactionBatchProcessor::validate_transaction_nonce_and_fee_payer` [1](#0-0) , which — prior to any instruction execution — calls `validate_transaction_nonce` to pre-advance the nonce ( [2](#0-1) ) and then `validate_transaction_fee_payer`, which debits the fee and builds a `RollbackAccounts` struct pairing the post-fee-debit fee payer state with the pre-advanced nonce state in one atomic unit ( [3](#0-2) , [4](#0-3) ).

At commit time, if the transaction's overall status is `Err` (any `InstructionError`, including one that occurs after a successful inner CPI to `AdvanceNonceAccount`), `update_accounts_for_failed_tx` discards whatever the real, in-flight account mutations were (including any CPI-driven nonce advance) and instead persists exactly the pre-computed `RollbackAccounts` pair — never the two independently [5](#0-4) , [6](#0-5) . This is exactly mirrored in `bank.rs`'s `create_commit_results`, which uses `rollback_accounts.fee_payer()` for the committed post-balance on failure [7](#0-6) .

So the attacker's proposed sequence — CPI advances nonce, then outer instruction fails — cannot decouple the two: whatever the CPI did to the on-chain nonce account is thrown away on failure, and the canonical `RollbackAccounts::SameNonceAndFeePayer`/`SeparateNonceAndFeePayer` (built together, atomically) is what's committed. Existing tests (`test_nonce_transaction`, `test_nonce_payer`, and the `svm/tests/integration_test.rs` SIMD-83 test suite) explicitly assert "fee charged and nonce has advanced" together on `InstructionError` paths [8](#0-7) , and the account-saver unit tests directly assert that only the rollback pair is persisted on failure regardless of any other writable-account mutation [9](#0-8) .

### Impact Explanation
None. The coupling invariant the question worries about breaking is enforced by a structurally different mechanism (`RollbackAccounts`, computed pre-execution and applied atomically at commit) that is entirely independent of CPI-exit synchronization ordering in `cpi.rs`. There is no code path by which `update_caller_account`'s timing affects bank-level commit decisions.

### Likelihood Explanation
Not applicable — the described call sequence does not create the alleged decoupling; the exploit precondition (successful CPI-nonce-advance value being independently committed alongside a separately-decided fee debit) does not exist in this codebase's architecture.

### Recommendation
No fix required. If auditors want additional assurance, an integration test can be added to `svm/tests/integration_test.rs` in the SIMD-83 test module specifically covering CPI-invoked `AdvanceNonceAccount` followed by an outer instruction error, verifying that the final committed nonce account state equals the pre-computed `RollbackAccounts` nonce state (not the CPI-advanced one) and that the fee payer debit matches `FeeDetails::total_fee()` exactly once — but this is a coverage improvement, not a vulnerability fix.

### Proof of Concept
N/A — no exploitable code path found. The relevant existing test `test_collect_accounts_for_failed_tx_rollback_separate_nonce_and_fee_payer` ( [10](#0-9) ) already demonstrates that on `InstructionError`, only the pre-computed `rollback_accounts` pair (nonce + fee payer) is persisted, regardless of what other writable accounts (including ones touched by inner CPI) contain.

### Citations

**File:** svm/src/transaction_processor.rs (L606-620)
```rust
                        }
                        // If the transaction failed & drop on failure is set then we don't want to
                        // update the accounts as this transaction will be dropped from the batch.
                        (Err(err), true) => Err(err.clone()),
                        // Unsuccessful transactions will still update rollback accounts (fee payer,
                        // nonce, etc).
                        (Err(_), false) => {
                            account_loader.update_accounts_for_failed_tx(
                                &executed_tx.loaded_transaction.rollback_accounts,
                                self.slot,
                            );

                            Ok(ProcessedTransaction::Executed(Box::new(executed_tx)))
                        }
                    }
```

**File:** svm/src/transaction_processor.rs (L694-731)
```rust
    fn validate_transaction_nonce_and_fee_payer<CB: TransactionProcessingCallback>(
        account_loader: &mut AccountLoader<CB>,
        message: &impl SVMMessage,
        checked_details: CheckedTransactionDetails,
        environment_blockhash: &Hash,
        next_lamports_per_signature: u64,
        rent: &Rent,
        relax_post_exec_min_balance_check: bool,
        strict_nonce_size_check: bool,
        error_counters: &mut TransactionErrorMetrics,
    ) -> TransactionValidationResult {
        let CheckedTransactionDetails {
            nonce_address,
            compute_budget_and_limits,
        } = checked_details;

        // If this is a nonce transaction, validate the nonce info.
        // This must be done for every transaction to support SIMD83 because
        // it may have changed due to use, authorization, or deallocation.
        let nonce_info = if let Some(ref nonce_address) = nonce_address {
            let next_durable_nonce = DurableNonce::from_blockhash(environment_blockhash);
            let nonce_result = Self::validate_transaction_nonce(
                account_loader,
                message,
                nonce_address,
                &next_durable_nonce,
                next_lamports_per_signature,
                strict_nonce_size_check,
                error_counters,
            );

            match nonce_result {
                Ok(nonce_info) => Some(nonce_info),
                Err(e) => return TransactionValidationResult::Unprocessable(e),
            }
        } else {
            None
        };
```

**File:** svm/src/transaction_processor.rs (L815-822)
```rust
        // Capture fee-subtracted fee payer account and next nonce account state
        // to commit if transaction execution fails.
        let rollback_accounts = RollbackAccounts::new(
            nonce_info,
            *fee_payer_address,
            loaded_fee_payer.account.clone(),
            fee_payer_loaded_rent_epoch,
        );
```

**File:** svm/src/transaction_processor.rs (L877-887)
```rust
        if nonce_can_be_advanced && nonce_authority_is_valid {
            let next_nonce_state = NonceState::new_initialized(
                &nonce_data.authority,
                *next_durable_nonce,
                next_lamports_per_signature,
            );
            nonce_account
                .set_state(&NonceVersions::new(next_nonce_state))
                .expect("Serializing into a validated nonce account cannot fail");

            Ok(NonceInfo::new(*nonce_address, nonce_account))
```

**File:** svm/src/rollback_accounts.rs (L65-100)
```rust
    pub(crate) fn new(
        nonce: Option<NonceInfo>,
        fee_payer_address: Pubkey,
        mut fee_payer_account: AccountSharedData,
        fee_payer_loaded_rent_epoch: Epoch,
    ) -> Self {
        if let Some(nonce) = nonce {
            if &fee_payer_address == nonce.address() {
                // `nonce` contains an AccountSharedData which has already been advanced to the current DurableNonce
                // `fee_payer_account` is an AccountSharedData as it currently exists on-chain
                // thus if the nonce account is being used as the fee payer, we need to update that data here
                // so we capture both the data change for the nonce and the lamports/rent epoch change for the fee payer
                fee_payer_account.set_data_from_slice(nonce.account().data());

                RollbackAccounts::SameNonceAndFeePayer {
                    nonce: (fee_payer_address, fee_payer_account),
                }
            } else {
                RollbackAccounts::SeparateNonceAndFeePayer {
                    nonce: (nonce.address, nonce.account),
                    fee_payer: (fee_payer_address, fee_payer_account),
                }
            }
        } else {
            // When rolling back failed transactions which don't use nonces, the
            // runtime should not update the fee payer's rent epoch so reset the
            // rollback fee payer account's rent epoch to its originally loaded
            // rent epoch value. In the future, a feature gate could be used to
            // alter this behavior such that rent epoch updates are handled the
            // same for both nonce and non-nonce failed transactions.
            fee_payer_account.set_rent_epoch(fee_payer_loaded_rent_epoch);
            RollbackAccounts::FeePayerOnly {
                fee_payer: (fee_payer_address, fee_payer_account),
            }
        }
    }
```

**File:** svm/src/account_loader.rs (L298-307)
```rust
    pub(crate) fn update_accounts_for_failed_tx(
        &mut self,
        rollback_accounts: &RollbackAccounts,
        current_slot: Slot,
    ) {
        for (account_address, account) in rollback_accounts {
            self.loaded_accounts
                .insert(*account_address, (account.clone(), current_slot));
        }
    }
```

**File:** runtime/src/bank.rs (L4472-4477)
```rust
                        // Rollback value is used for failure.
                        let fee_payer_post_balance = if successful {
                            loaded_accounts[0].1.lamports()
                        } else {
                            rollback_accounts.fee_payer().1.lamports()
                        };
```

**File:** runtime/src/bank/tests.rs (L4194-4204)
```rust
    /* Check fee charged and nonce has advanced */
    let mut recent_message = nonce_tx.message.clone();
    recent_message.recent_blockhash = bank.last_blockhash();
    expected_balance -= bank
        .get_fee_for_message(&new_sanitized_message(recent_message))
        .unwrap();
    assert_eq!(bank.get_balance(&custodian_pubkey), expected_balance);
    assert_ne!(
        nonce_hash,
        get_nonce_blockhash(&bank, &nonce_pubkey).unwrap()
    );
```

**File:** runtime/src/account_saver.rs (L456-524)
```rust
    fn test_collect_accounts_for_failed_tx_rollback_separate_nonce_and_fee_payer() {
        let nonce_address = Pubkey::new_unique();
        let nonce_authority = keypair_from_seed(&[0; 32]).unwrap();
        let from = keypair_from_seed(&[1; 32]).unwrap();
        let from_address = from.pubkey();
        let to_address = Pubkey::new_unique();
        let durable_nonce = DurableNonce::from_blockhash(&Hash::new_unique());
        let nonce_state = NonceVersions::new(NonceState::Initialized(NonceData::new(
            nonce_authority.pubkey(),
            durable_nonce,
            0,
        )));
        let nonce_account_post =
            AccountSharedData::new_data(43, &nonce_state, &system_program::id()).unwrap();
        let from_account_post = AccountSharedData::new(4199, 0, &Pubkey::default());
        let to_account = AccountSharedData::new(2, 0, &Pubkey::default());
        let nonce_authority_account = AccountSharedData::new(3, 0, &Pubkey::default());
        let recent_blockhashes_sysvar_account = AccountSharedData::new(4, 0, &Pubkey::default());

        let instructions = vec![
            system_instruction::advance_nonce_account(&nonce_address, &nonce_authority.pubkey()),
            system_instruction::transfer(&from_address, &to_address, 42),
        ];
        let message = Message::new(&instructions, Some(&from_address));
        let blockhash = Hash::new_unique();
        let transaction_accounts = vec![
            (message.account_keys[0], from_account_post),
            (message.account_keys[1], nonce_authority_account),
            (message.account_keys[2], nonce_account_post),
            (message.account_keys[3], to_account),
            (message.account_keys[4], recent_blockhashes_sysvar_account),
        ];
        let tx = new_sanitized_tx(&[&nonce_authority, &from], message, blockhash);

        let durable_nonce = DurableNonce::from_blockhash(&Hash::new_unique());
        let nonce_state = NonceVersions::new(NonceState::Initialized(NonceData::new(
            nonce_authority.pubkey(),
            durable_nonce,
            0,
        )));
        let nonce_account_pre =
            AccountSharedData::new_data(42, &nonce_state, &system_program::id()).unwrap();
        let from_account_pre = AccountSharedData::new(4242, 0, &Pubkey::default());

        let touched_flags =
            touched_flags_for_test(transaction_accounts.len(), transaction_accounts.len());
        let loaded = LoadedTransaction {
            accounts: transaction_accounts,
            // Worst case: every writable account appears modified, yet a failed
            // tx must still persist only its rollback accounts.
            touched_flags,
            fee_details: FeeDetails::default(),
            rollback_accounts: RollbackAccounts::SeparateNonceAndFeePayer {
                nonce: (nonce_address, nonce_account_pre.clone()),
                fee_payer: (from_address, from_account_pre.clone()),
            },
            compute_budget: SVMTransactionExecutionBudget::default(),
            loaded_accounts_data_size: 0,
        };

        let txs = vec![tx];
        let processing_results = vec![new_executed_processing_result(
            Err(TransactionError::InstructionError(
                1,
                InstructionError::InvalidArgument,
            )),
            loaded,
        )];
        let max_collected_accounts = max_number_of_accounts_to_collect(&txs, &processing_results);
```
