# [?] metrics, bankf: fix metrics oob in bankf

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-09-29
Source: https://github.com/firedancer-io/firedancer/commit/f5b42ccf5579250d6e80171d49857212d5cf48fe
Type: security-commit

## Details
metrics, bankf: fix metrics oob in bankf

bug found by @intrigus-lgtm; fixed by using the correct enum for the counter in metrics.xml and then using the generated enum values, instead of redefining them and risking drift.

## Patch
### book/api/metrics-generated.md
```diff
@@ -987,47 +987,29 @@
 
 | Metric | Type | Description |
 |--------|------|-------------|
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">success</span>"} | counter | Result of loading and executing a transaction. (Success) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">account_&#8203;in_&#8203;use</span>"} | counter | Result of loading and executing a transaction. (An account is already being processed in another transaction in a way that does not support parallelism.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">account_&#8203;loaded_&#8203;twice</span>"} | counter | Result of loading and executing a transaction. (A `Pubkey` appears twice in the transaction's `account_keys`.  Instructions can reference `Pubkey`s more than once but the message must contain a list with no duplicate keys.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">account_&#8203;not_&#8203;found</span>"} | counter | Result of loading and executing a transaction. (Attempt to debit an account but found no record of a prior credit.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">program_&#8203;account_&#8203;not_&#8203;found</span>"} | counter | Result of loading and executing a transaction. (Attempt to load a program that does not exist.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">insufficient_&#8203;funds_&#8203;for_&#8203;fee</span>"} | counter | Result of loading and executing a transaction. (The fee payer `Pubkey` does not have sufficient balance to pay the fee to schedule the transaction.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;account_&#8203;for_&#8203;fee</span>"} | counter | Result of loading and executing a transaction. (This account may not be used to pay transaction fees.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">already_&#8203;processed</span>"} | counter | Result of loading and executing a transaction. (The bank has seen this transaction before. This can occur under normal operation when a UDP packet is duplicated, as a user error from a client not updating its `recent_blockhash`, or as a double-spend attack.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">blockhash_&#8203;not_&#8203;found</span>"} | counter | Result of loading and executing a transaction. (The bank has not seen the given `recent_blockhash` or the transaction is too old and the `recent_blockhash` has been discarded.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">instruction_&#8203;error</span>"} | counter | Result of loading and executing a transaction. (An error occurred while processing an instruction.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">call_&#8203;chain_&#8203;too_&#8203;deep</span>"} | counter | Result of loading and executing a transaction. (Loader call chain is too deep.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">missing_&#8203;signature_&#8203;for_&#8203;fee</span>"} | counter | Result of loading and executing a transaction. (Transaction requires a fee but has no signature present.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;account_&#8203;index</span>"} | counter | Result of loading and executing a transaction. (Transaction contains an invalid account reference.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">signature_&#8203;failure</span>"} | counter | Result of loading and executing a transaction. (Transaction did not pass signature verification.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;program_&#8203;for_&#8203;execution</span>"} | counter | Result of loading and executing a transaction. (This program may not be used for executing instructions.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">sanitize_&#8203;failure</span>"} | counter | Result of loading and executing a transaction. (Transaction failed to sanitize accounts offsets correctly implies that account locks are not taken for this TX, and should not be unlocked.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">cluster_&#8203;maintenance</span>"} | counter | Result of loading and executing a transaction. (Transactions are currently disabled due to cluster maintenance.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">account_&#8203;borrow_&#8203;outstanding</span>"} | counter | Result of loading and executing a transaction. (Transaction processing left an account with an outstanding borrowed reference.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">would_&#8203;exceed_&#8203;max_&#8203;block_&#8203;cost_&#8203;limit</span>"} | counter | Result of loading and executing a transaction. (Transaction would exceed max Block Cost Limit.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">unsupported_&#8203;version</span>"} | counter | Result of loading and executing a transaction. (Transaction version is unsupported.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;writable_&#8203;account</span>"} | counter | Result of loading and executing a transaction. (Transaction loads a writable account that cannot be written.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">would_&#8203;exceed_&#8203;max_&#8203;account_&#8203;cost_&#8203;limit</span>"} | counter | Result of loading and executing a transaction. (Transaction would exceed max account limit within the block.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">would_&#8203;exceed_&#8203;account_&#8203;data_&#8203;block_&#8203;limit</span>"} | counter | Result of loading and executing a transaction. (Transaction would exceed account data limit within the block.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">too_&#8203;many_&#8203;account_&#8203;locks</span>"} | counter | Result of loading and executing a transaction. (Transaction locked too many accounts.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">address_&#8203;lookup_&#8203;table_&#8203;not_&#8203;found</span>"} | counter | Result of loading and executing a transaction. (Address lookup table not found.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;address_&#8203;lookup_&#8203;table_&#8203;owner</span>"} | counter | Result of loading and executing a transaction. (Attempted to lookup addresses from an account owned by the wrong program.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;address_&#8203;lookup_&#8203;table_&#8203;data</span>"} | counter | Result of loading and executing a transaction. (Attempted to lookup addresses from an invalid account.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;address_&#8203;lookup_&#8203;table_&#8203;index</span>"} | counter | Result of loading and executing a transaction. (Address table lookup uses an invalid index.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;rent_&#8203;paying_&#8203;account</span>"} | counter | Result of loading and executing a transaction. (Transaction leaves an account with a lower balance than rent-exempt minimum.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">would_&#8203;exceed_&#8203;max_&#8203;vote_&#8203;cost_&#8203;limit</span>"} | counter | Result of loading and executing a transaction. (Transaction would exceed max Vote Cost Limit.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">would_&#8203;exceed_&#8203;account_&#8203;data_&#8203;total_&#8203;limit</span>"} | counter | Result of loading and executing a transaction. (Transaction would exceed total account data limit.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">duplicate_&#8203;instruction</span>"} | counter | Result of loading and executing a transaction. (Transaction contains a duplicate instruction that is not allowed.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">insufficient_&#8203;funds_&#8203;for_&#8203;rent</span>"} | counter | Result of loading and executing a transaction. (Transaction results in an account with insufficient funds for rent.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">max_&#8203;loaded_&#8203;accounts_&#8203;data_&#8203;size_&#8203;exceeded</span>"} | counter | Result of loading and executing a transaction. (Transaction exceeded max loaded accounts data size cap.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">invalid_&#8203;loaded_&#8203;accounts_&#8203;data_&#8203;size_&#8203;limit</span>"} | counter | Result of loading and executing a transaction. (LoadedAccountsDataSizeLimit set for transaction must be greater than 0.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">resanitization_&#8203;needed</span>"} | counter | Result of loading and executing a transaction. (Sanitized transaction differed before/after feature activation. Needs to be resanitized.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">program_&#8203;execution_&#8203;temporarily_&#8203;restricted</span>"} | counter | Result of loading and executing a transaction. (Program execution is temporarily restricted on an account.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">unbalanced_&#8203;transaction</span>"} | counter | Result of loading and executing a transaction. (The total balance before the transaction does not equal the total balance after the transaction.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">program_&#8203;cache_&#8203;hit_&#8203;max_&#8203;limit</span>"} | counter | Result of loading and executing a transaction. (The total program cache size hit the maximum allowed limit.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">commit_&#8203;cancelled</span>"} | counter | Result of loading and executing a transaction. (The process for committing the transaction was cancelled internally.) |
-| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;error="<span class="metrics-enum">bundle_&#8203;peer</span>"} | counter | Result of loading and executing a transaction. (Transaction is part of a bundle and one of the peer transactions failed.) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">success</span>"} | counter | Result of loading and executing a transaction. (Transaction executed successfully) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">instructon_&#8203;error</span>"} | counter | Result of loading and executing a transaction. (An error occurred while processing an instruction) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">account_&#8203;not_&#8203;found</span>"} | counter | Result of loading and executing a transaction. (The transaction fee payer address was not found) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">program_&#8203;account_&#8203;not_&#8203;found</span>"} | counter | Result of loading and executing a transaction. (A program account referenced by the transaction was not found) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">insufficient_&#8203;funds_&#8203;for_&#8203;fee</span>"} | counter | Result of loading and executing a transaction. (The transaction fee payer did not have balance to pay the fee) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">invalid_&#8203;account_&#8203;for_&#8203;fee</span>"} | counter | Result of loading and executing a transaction. (The transaction fee payer account is not owned by the system program, or has data that is not a nonce) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">already_&#8203;processed</span>"} | counter | Result of loading and executing a transaction. (The transaction has already been processed in a recent block) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">blockhash_&#8203;not_&#8203;found</span>"} | counter | Result of loading and executing a transaction. (The transaction references a blockhash that is not recent, or advances a nonce with the wrong value) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">invalid_&#8203;program_&#8203;for_&#8203;execution</span>"} | counter | Result of loading and executing a transaction. (A program account referenced by the transaction was no executable. TODO: No longer needed with SIMD-0162) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">address_&#8203;lookup_&#8203;table_&#8203;not_&#8203;found</span>"} | counter | Result of loading and executing a transaction. (The transaction references an ALUT account that does not exist or is inactive) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">invalid_&#8203;address_&#8203;lookup_&#8203;table_&#8203;owner</span>"} | counter | Result of loading and executing a transaction. (The transaction references an ALUT account that is not owned by the ALUT program account) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">invalid_&#8203;address_&#8203;lookup_&#8203;table_&#8203;data</span>"} | counter | Result of loading and executing a transaction. (The transaction references an ALUT account that contains data which is not a valid ALUT) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">invalid_&#8203;address_&#8203;lookup_&#8203;table_&#8203;index</span>"} | counter | Result of loading and executing a transaction. (The transaction references an account offset from the ALUT which does not exist) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">max_&#8203;loaded_&#8203;accounts_&#8203;data_&#8203;size_&#8203;exceeded</span>"} | counter | Result of loading and executing a transaction. (The total account data size of the loaded accounts exceeds the consensus limit) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">duplicate_&#8203;instruction</span>"} | counter | Result of loading and executing a transaction. (A compute budget program instruction was invoked more than once) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">invalid_&#8203;loaded_&#8203;accounts_&#8203;data_&#8203;size_&#8203;limit</span>"} | counter | Result of loading and executing a transaction. (The compute budget program was invoked and set the loaded accounts data size to zero) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">account_&#8203;in_&#8203;use</span>"} | counter | Result of loading and executing a transaction. (The transaction conflicts with another transaction in the microblock. TODO: No longer possible with smart dispatcher) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">account_&#8203;loaded_&#8203;twice</span>"} | counter | Result of loading and executing a transaction. (The transaction references the same account twice) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">signature_&#8203;failure</span>"} | counter | Result of loading and executing a transaction. (The transaction had an invalid signature) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">too_&#8203;many_&#8203;account_&#8203;locks</span>"} | counter | Result of loading and executing a transaction. (The transaction references too many accounts. TODO: No longer possible with smart dispatcher) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">insufficient_&#8203;funds_&#8203;for_&#8203;rent</span>"} | counter | Result of loading and executing a transaction. (The transaction would leave an account with a lower balance than the rent-exempt minimum) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">unbalanced_&#8203;transaction</span>"} | counter | Result of loading and executing a transaction. (The total referenced account lamports before and after the transaction was unbalanced) |
+| <span class="metrics-name">bankf_&#8203;transaction_&#8203;result</span><br/>{transaction_&#8203;result="<span class="metrics-enum">bundle_&#8203;peer</span>"} | counter | Result of loading and executing a transaction. (The transaction was part of a bundle and an earlier transaction in the bundle failed) |
 
 </div>
 
```

### src/disco/metrics/generated/fd_metrics_bankf.c
```diff
@@ -2,45 +2,27 @@
 #include "fd_metrics_bankf.h"
 
 const fd_metrics_meta_t FD_METRICS_BANKF[FD_METRICS_BANKF_TOTAL] = {
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, SUCCESS ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, ACCOUNT_IN_USE ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, ACCOUNT_LOADED_TWICE ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, ACCOUNT_NOT_FOUND ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, PROGRAM_ACCOUNT_NOT_FOUND ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INSUFFICIENT_FUNDS_FOR_FEE ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_ACCOUNT_FOR_FEE ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, ALREADY_PROCESSED ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, BLOCKHASH_NOT_FOUND ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INSTRUCTION_ERROR ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, CALL_CHAIN_TOO_DEEP ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, MISSING_SIGNATURE_FOR_FEE ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_ACCOUNT_INDEX ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, SIGNATURE_FAILURE ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_PROGRAM_FOR_EXECUTION ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, SANITIZE_FAILURE ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, CLUSTER_MAINTENANCE ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, ACCOUNT_BORROW_OUTSTANDING ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, WOULD_EXCEED_MAX_BLOCK_COST_LIMIT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, UNSUPPORTED_VERSION ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_WRITABLE_ACCOUNT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, WOULD_EXCEED_MAX_ACCOUNT_COST_LIMIT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, WOULD_EXCEED_ACCOUNT_DATA_BLOCK_LIMIT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, TOO_MANY_ACCOUNT_LOCKS ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, ADDRESS_LOOKUP_TABLE_NOT_FOUND ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_ADDRESS_LOOKUP_TABLE_OWNER ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_ADDRESS_LOOKUP_TABLE_DATA ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_ADDRESS_LOOKUP_TABLE_INDEX ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_RENT_PAYING_ACCOUNT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, WOULD_EXCEED_MAX_VOTE_COST_LIMIT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, WOULD_EXCEED_ACCOUNT_DATA_TOTAL_LIMIT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, DUPLICATE_INSTRUCTION ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INSUFFICIENT_FUNDS_FOR_RENT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, RESANITIZATION_NEEDED ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, PROGRAM_EXECUTION_TEMPORARILY_RESTRICTED ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, UNBALANCED_TRANSACTION ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, PROGRAM_CACHE_HIT_MAX_LIMIT ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, COMMIT_CANCELLED ),
-    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_ERROR, BUNDLE_PEER ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, SUCCESS ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INSTRUCTON_ERROR ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, ACCOUNT_NOT_FOUND ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, PROGRAM_ACCOUNT_NOT_FOUND ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INSUFFICIENT_FUNDS_FOR_FEE ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INVALID_ACCOUNT_FOR_FEE ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, ALREADY_PROCESSED ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, BLOCKHASH_NOT_FOUND ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INVALID_PROGRAM_FOR_EXECUTION ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, ADDRESS_LOOKUP_TABLE_NOT_FOUND ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INVALID_ADDRESS_LOOKUP_TABLE_OWNER ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INVALID_ADDRESS_LOOKUP_TABLE_DATA ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INVALID_ADDRESS_LOOKUP_TABLE_INDEX ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, DUPLICATE_INSTRUCTION ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, ACCOUNT_IN_USE ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, ACCOUNT_LOADED_TWICE ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, SIGNATURE_FAILURE ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, TOO_MANY_ACCOUNT_LOCKS ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, INSUFFICIENT_FUNDS_FOR_RENT ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, UNBALANCED_TRANSACTION ),
+    DECLARE_METRIC_ENUM( BANKF_TRANSACTION_RESULT, COUNTER, TRANSACTION_RESULT, BUNDLE_PEER ),
 };
```

### src/disco/metrics/generated/fd_metrics_bankf.h
```diff
@@ -8,49 +8,31 @@
 #define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_TYPE (FD_METRICS_TYPE_COUNTER)
 #define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_DESC "Result of loading and executing a transaction."
 #define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_CVT  (FD_METRICS_CONVERTER_NONE)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_CNT  (41UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_CNT  (23UL)
 
 #define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_SUCCESS_OFF (16UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ACCOUNT_IN_USE_OFF (17UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ACCOUNT_LOADED_TWICE_OFF (18UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ACCOUNT_NOT_FOUND_OFF (19UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_PROGRAM_ACCOUNT_NOT_FOUND_OFF (20UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INSUFFICIENT_FUNDS_FOR_FEE_OFF (21UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ACCOUNT_FOR_FEE_OFF (22UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ALREADY_PROCESSED_OFF (23UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_BLOCKHASH_NOT_FOUND_OFF (24UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INSTRUCTION_ERROR_OFF (25UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_CALL_CHAIN_TOO_DEEP_OFF (26UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_MISSING_SIGNATURE_FOR_FEE_OFF (27UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ACCOUNT_INDEX_OFF (28UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_SIGNATURE_FAILURE_OFF (29UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_PROGRAM_FOR_EXECUTION_OFF (30UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_SANITIZE_FAILURE_OFF (31UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_CLUSTER_MAINTENANCE_OFF (32UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ACCOUNT_BORROW_OUTSTANDING_OFF (33UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_WOULD_EXCEED_MAX_BLOCK_COST_LIMIT_OFF (34UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_UNSUPPORTED_VERSION_OFF (35UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_WRITABLE_ACCOUNT_OFF (36UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_WOULD_EXCEED_MAX_ACCOUNT_COST_LIMIT_OFF (37UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_WOULD_EXCEED_ACCOUNT_DATA_BLOCK_LIMIT_OFF (38UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_TOO_MANY_ACCOUNT_LOCKS_OFF (39UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ADDRESS_LOOKUP_TABLE_NOT_FOUND_OFF (40UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ADDRESS_LOOKUP_TABLE_OWNER_OFF (41UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ADDRESS_LOOKUP_TABLE_DATA_OFF (42UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ADDRESS_LOOKUP_TABLE_INDEX_OFF (43UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_RENT_PAYING_ACCOUNT_OFF (44UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_WOULD_EXCEED_MAX_VOTE_COST_LIMIT_OFF (45UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_WOULD_EXCEED_ACCOUNT_DATA_TOTAL_LIMIT_OFF (46UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_DUPLICATE_INSTRUCTION_OFF (47UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INSUFFICIENT_FUNDS_FOR_RENT_OFF (48UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED_OFF (49UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT_OFF (50UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_RESANITIZATION_NEEDED_OFF (51UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_PROGRAM_EXECUTION_TEMPORARILY_RESTRICTED_OFF (52UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_UNBALANCED_TRANSACTION_OFF (53UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_PROGRAM_CACHE_HIT_MAX_LIMIT_OFF (54UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_COMMIT_CANCELLED_OFF (55UL)
-#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_BUNDLE_PEER_OFF (56UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INSTRUCTON_ERROR_OFF (17UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ACCOUNT_NOT_FOUND_OFF (18UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_PROGRAM_ACCOUNT_NOT_FOUND_OFF (19UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INSUFFICIENT_FUNDS_FOR_FEE_OFF (20UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ACCOUNT_FOR_FEE_OFF (21UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ALREADY_PROCESSED_OFF (22UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_BLOCKHASH_NOT_FOUND_OFF (23UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_PROGRAM_FOR_EXECUTION_OFF (24UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ADDRESS_LOOKUP_TABLE_NOT_FOUND_OFF (25UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ADDRESS_LOOKUP_TABLE_OWNER_OFF (26UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ADDRESS_LOOKUP_TABLE_DATA_OFF (27UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_ADDRESS_LOOKUP_TABLE_INDEX_OFF (28UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED_OFF (29UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_DUPLICATE_INSTRUCTION_OFF (30UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT_OFF (31UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ACCOUNT_IN_USE_OFF (32UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_ACCOUNT_LOADED_TWICE_OFF (33UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_SIGNATURE_FAILURE_OFF (34UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_TOO_MANY_ACCOUNT_LOCKS_OFF (35UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_INSUFFICIENT_FUNDS_FOR_RENT_OFF (36UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_UNBALANCED_TRANSACTION_OFF (37UL)
+#define FD_METRICS_COUNTER_BANKF_TRANSACTION_RESULT_BUNDLE_PEER_OFF (38UL)
 
-#define FD_METRICS_BANKF_TOTAL (41UL)
+#define FD_METRICS_BANKF_TOTAL (23UL)
 extern const fd_metrics_meta_t FD_METRICS_BANKF[FD_METRICS_BANKF_TOTAL];
```

### src/disco/metrics/metrics.xml
```diff
@@ -631,7 +631,16 @@ metric introduced.
 
 <enum name="TransactionResult">
     <int value="0" name="Success" label="Transaction executed successfully" />
+
+    <!-- Preflight and execution errors. This is just instruction
+         error, which can occur both when loading the transaction, and
+         when executing it. When loading, it occurs when executing the
+         compute budget program, or verifying precompiles. -->
     <int value="1" name="InstructonError" label="An error occurred while processing an instruction" />
+
+    <!-- Preflight errors. These are errors in validation before we
+         begin actually executing the transaction in the virtual
+         machine. -->
     <int value="2" name="AccountNotFound" label="The transaction fee payer address was not found" />
     <int value="3" name="ProgramAccountNotFound" label="A program account referenced by the transaction was not found" />
     <int value="4" name="InsufficientFundsForFee" label="The transaction fee payer did not have balance to pay the fee" />
@@ -646,17 +655,29 @@ metric introduced.
     <int value="13" name="MaxLoadedAccountsDataSizeExceeded" label="The total account data size of the loaded accounts exceeds the consensus limit" />
     <int value="14" name="DuplicateInstruction" label="A compute budget program instruction was invoked more than once" />
     <int value="15" name="InvalidLoadedAccountsDataSizeLimit" label="The compute budget program was invoked and set the loaded accounts data size to zero" />
+
+    <!-- Preflight errors during replay. These are errors in validation
+         before we begin executing the transaction, which can only
+         occur during replay, as such transactions do not make it to
+         execution when we are leader. -->
     <int value="16" name="AccountInUse" label="The transaction conflicts with another transaction in the microblock. TODO: No longer possible with smart dispatcher" />
     <int value="17" name="AccountLoadedTwice" label="The transaction references the same account twice" />
     <int value="18" name="SignatureFailure" label="The transaction had an invalid signature" />
     <int value="19" name="TooManyAccountLocks" label="The transaction references too many accounts. TODO: No longer possible with smart dispatcher" />
+
+    <!-- Execution errors. These are errors which occur during actual
+         execution of the transaction, after it has been validated. -->
     <int value="20" name="InsufficientFundsForRent" label="The transaction would leave an account with a lower balance than the rent-exempt minimum" />
     <int value="21" name="UnbalancedTransaction" label="The total referenced account lamports before and after the transaction was unbalanced" />
+
+    <!-- Errors that aren't returned by the runtime execution itself,
+         but are used by bank as an additional reason transactions
+         might fail. -->
     <int value="22" name="BundlePeer" label="The transaction was part of a bundle and an earlier transaction in the bundle failed" />
 </enum>
 
 <tile name="bankf">
-    <counter name="TransactionResult" enum="TransactionError" summary="Result of loading and executing a transaction." />
+    <counter name="TransactionResult" enum="TransactionResult" summary="Result of loading and executing a transaction." />
 </tile>
 
 <tile name="bank">
```

### src/discof/bank/fd_bank_err.h
```diff
@@ -3,83 +3,38 @@
 
 #include "../../util/log/fd_log.h"
 #include "../../flamenco/runtime/fd_runtime_err.h"
+#include "../../disco/metrics/generated/fd_metrics_enums.h"
 
-#define FD_BANK_EXECUTE_SUCCESS                                     0
-
-/* Preflight and execution errors.  This is just instruction error,
-   which can occur both when loading the transaction, and when executing
-   it.  When loading, it occurs when executing the compute budget
-   program, or verifying precompiles. */
-#define FD_BANK_TXN_ERR_INSTRUCTION_ERROR                          -1
-
-/* Preflight errors.  These are errors in validation before we begin
-   actually executing the transaction in the virtual machine. */
-#define FD_BANK_TXN_ERR_ACCOUNT_NOT_FOUND                          -2 /* The transaction fee payer address was not found */
-#define FD_BANK_TXN_ERR_PROGRAM_ACCOUNT_NOT_FOUND                  -3 /* A program account referenced by the transaction was not found */
-#define FD_BANK_TXN_ERR_INSUFFICIENT_FUNDS_FOR_FEE                 -4 /* The transaction fee payer did not have balance to pay the fee */
-#define FD_BANK_TXN_ERR_INVALID_ACCOUNT_FOR_FEE                    -5 /* The transaction fee payer account is not owned by the system program, or has data that is not a nonce */
-#define FD_BANK_TXN_ERR_ALREADY_PROCESSED                          -6 /* The transaction has already been processed in a recent block */
-#define FD_BANK_TXN_ERR_BLOCKHASH_NOT_FOUND                        -7 /* The transaction references a blockhash that is not recent, or advances a nonce with the wrong value */
-#define FD_BANK_TXN_ERR_INVALID_PROGRAM_FOR_EXECUTION              -8 /* A program account referenced by the transaction was no executable. TODO: No longer needed with SIMD-0162 */
-#define FD_BANK_TXN_ERR_ADDRESS_LOOKUP_TABLE_NOT_FOUND             -9 /* The transaction references an ALUT account that does not exist or is inactive */
-#define FD_BANK_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_OWNER        -10 /* The transaction references an ALUT account that is not owned by the ALUT program account */
-#define FD_BANK_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_DATA         -11 /* The transaction references an ALUT account that contains data which is not a valid ALUT */
-#define FD_BANK_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_INDEX        -12 /* The transaction references an account offset from the ALUT which does not exist */
-#define FD_BANK_TXN_ERR_MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED    -13 /* The total account data size of the loaded accounts exceeds the consensus limit */
-#define FD_BANK_TXN_ERR_DUPLICATE_INSTRUCTION                     -14 /* A compute budget program instruction was invoked more than once */
-#define FD_BANK_TXN_ERR_INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT   -15 /* The compute budget program was invoked and set the loaded accounts data size to zero */
-
-/* Preflight errors during replay.  These are errors in validation
-   before we begin executing the transaction, which can only occur
-   during replay, as such transactions do not make it to execution when
-   we are leader. */
-#define FD_BANK_TXN_ERR_ACCOUNT_IN_USE                            -16 /* The transaction conflicts with another transaction in the microblock. TODO: No longer possible with smart dispatcher */
-#define FD_BANK_TXN_ERR_ACCOUNT_LOADED_TWICE                      -17 /* The transaction references the same account twice */
-#define FD_BANK_TXN_ERR_SIGNATURE_FAILURE                         -18 /* The transaction had an invalid signature */
-#define FD_BANK_TXN_ERR_TOO_MANY_ACCOUNT_LOCKS                    -19 /* The transaction references too many accounts. TODO: No longer possible with smart dispatcher */
-
-/* Execution errors.  These are errors which occur during actual
-   execution of the transaction, after it has been validated. */
-#define FD_BANK_TXN_ERR_INSUFFICIENT_FUNDS_FOR_RENT               -20 /* The transaction would leave an account with a lower balance than the rent-exempt minimum */
-#define FD_BANK_TXN_ERR_UNBALANCED_TRANSACTION                    -21 /* The total referenced account lamports before and after the transaction was unbalanced */
-
-/* Errors that aren't returned by the runtime execution itself, but are
-   used by bank as an additional reason transactions might fail. */
-#define FD_BANK_TXN_ERR_BUNDLE_PEER                               -22 /* The transaction was part of a bundle and an earlier transaction in the bundle failed */
-
-/* Marker for the lowest error number, must be updated when new errors
-   are added. */
-#define FD_BANK_TXN_ERR_LAST                                      -22
 
 static inline int
 fd_bank_err_from_runtime_err( int err ) {
    switch( err ) {
-      case FD_RUNTIME_EXECUTE_SUCCESS:                                 return FD_BANK_EXECUTE_SUCCESS;
-
-      case FD_RUNTIME_TXN_ERR_INSTRUCTION_ERROR:                       return FD_BANK_TXN_ERR_INSTRUCTION_ERROR;
-
-      case FD_RUNTIME_TXN_ERR_ACCOUNT_NOT_FOUND:                       return FD_BANK_TXN_ERR_ACCOUNT_NOT_FOUND;
-      case FD_RUNTIME_TXN_ERR_PROGRAM_ACCOUNT_NOT_FOUND:               return FD_BANK_TXN_ERR_PROGRAM_ACCOUNT_NOT_FOUND;
-      case FD_RUNTIME_TXN_ERR_INSUFFICIENT_FUNDS_FOR_FEE:              return FD_BANK_TXN_ERR_INSUFFICIENT_FUNDS_FOR_FEE;
-      case FD_RUNTIME_TXN_ERR_INVALID_ACCOUNT_FOR_FEE:                 return FD_BANK_TXN_ERR_INVALID_ACCOUNT_FOR_FEE;
-      case FD_RUNTIME_TXN_ERR_ALREADY_PROCESSED:                       return FD_BANK_TXN_ERR_ALREADY_PROCESSED;
-      case FD_RUNTIME_TXN_ERR_BLOCKHASH_NOT_FOUND:                     return FD_BANK_TXN_ERR_BLOCKHASH_NOT_FOUND;
-      case FD_RUNTIME_TXN_ERR_INVALID_PROGRAM_FOR_EXECUTION:           return FD_BANK_TXN_ERR_INVALID_PROGRAM_FOR_EXECUTION;
-      case FD_RUNTIME_TXN_ERR_ADDRESS_LOOKUP_TABLE_NOT_FOUND:          return FD_BANK_TXN_ERR_ADDRESS_LOOKUP_TABLE_NOT_FOUND;
-      case FD_RUNTIME_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_OWNER:      return FD_BANK_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_OWNER;
-      case FD_RUNTIME_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_DATA:       return FD_BANK_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_DATA;
-      case FD_RUNTIME_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_INDEX:      return FD_BANK_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_INDEX;
-      case FD_RUNTIME_TXN_ERR_MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED:  return FD_BANK_TXN_ERR_MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED;
-      case FD_RUNTIME_TXN_ERR_DUPLICATE_INSTRUCTION:                   return FD_BANK_TXN_ERR_DUPLICATE_INSTRUCTION;
-      case FD_RUNTIME_TXN_ERR_INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT: return FD_BANK_TXN_ERR_INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT;
-
-      case FD_RUNTIME_TXN_ERR_ACCOUNT_IN_USE:                          return FD_BANK_TXN_ERR_ACCOUNT_IN_USE;
-      case FD_RUNTIME_TXN_ERR_ACCOUNT_LOADED_TWICE:                    return FD_BANK_TXN_ERR_ACCOUNT_LOADED_TWICE;
-      case FD_RUNTIME_TXN_ERR_SIGNATURE_FAILURE:                       return FD_BANK_TXN_ERR_SIGNATURE_FAILURE;
-      case FD_RUNTIME_TXN_ERR_TOO_MANY_ACCOUNT_LOCKS:                  return FD_BANK_TXN_ERR_TOO_MANY_ACCOUNT_LOCKS;
-
-      case FD_RUNTIME_TXN_ERR_INSUFFICIENT_FUNDS_FOR_RENT:             return FD_BANK_TXN_ERR_INSUFFICIENT_FUNDS_FOR_RENT;
-      case FD_RUNTIME_TXN_ERR_UNBALANCED_TRANSACTION:                  return FD_BANK_TXN_ERR_UNBALANCED_TRANSACTION;
+      case FD_RUNTIME_EXECUTE_SUCCESS:                                 return FD_METRICS_ENUM_TRANSACTION_RESULT_V_SUCCESS_IDX;
+
+      case FD_RUNTIME_TXN_ERR_INSTRUCTION_ERROR:                       return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INSTRUCTON_ERROR_IDX;
+
+      case FD_RUNTIME_TXN_ERR_ACCOUNT_NOT_FOUND:                       return FD_METRICS_ENUM_TRANSACTION_RESULT_V_ACCOUNT_NOT_FOUND_IDX;
+      case FD_RUNTIME_TXN_ERR_PROGRAM_ACCOUNT_NOT_FOUND:               return FD_METRICS_ENUM_TRANSACTION_RESULT_V_PROGRAM_ACCOUNT_NOT_FOUND_IDX;
+      case FD_RUNTIME_TXN_ERR_INSUFFICIENT_FUNDS_FOR_FEE:              return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INSUFFICIENT_FUNDS_FOR_FEE_IDX;
+      case FD_RUNTIME_TXN_ERR_INVALID_ACCOUNT_FOR_FEE:                 return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INVALID_ACCOUNT_FOR_FEE_IDX;
+      case FD_RUNTIME_TXN_ERR_ALREADY_PROCESSED:                       return FD_METRICS_ENUM_TRANSACTION_RESULT_V_ALREADY_PROCESSED_IDX;
+      case FD_RUNTIME_TXN_ERR_BLOCKHASH_NOT_FOUND:                     return FD_METRICS_ENUM_TRANSACTION_RESULT_V_BLOCKHASH_NOT_FOUND_IDX;
+      case FD_RUNTIME_TXN_ERR_INVALID_PROGRAM_FOR_EXECUTION:           return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INVALID_PROGRAM_FOR_EXECUTION_IDX;
+      case FD_RUNTIME_TXN_ERR_ADDRESS_LOOKUP_TABLE_NOT_FOUND:          return FD_METRICS_ENUM_TRANSACTION_RESULT_V_ADDRESS_LOOKUP_TABLE_NOT_FOUND_IDX;
+      case FD_RUNTIME_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_OWNER:      return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INVALID_ADDRESS_LOOKUP_TABLE_OWNER_IDX;
+      case FD_RUNTIME_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_DATA:       return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INVALID_ADDRESS_LOOKUP_TABLE_DATA_IDX;
+      case FD_RUNTIME_TXN_ERR_INVALID_ADDRESS_LOOKUP_TABLE_INDEX:      return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INVALID_ADDRESS_LOOKUP_TABLE_INDEX_IDX;
+      case FD_RUNTIME_TXN_ERR_MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED:  return FD_METRICS_ENUM_TRANSACTION_RESULT_V_MAX_LOADED_ACCOUNTS_DATA_SIZE_EXCEEDED_IDX;
+      case FD_RUNTIME_TXN_ERR_DUPLICATE_INSTRUCTION:                   return FD_METRICS_ENUM_TRANSACTION_RESULT_V_DUPLICATE_INSTRUCTION_IDX;
+      case FD_RUNTIME_TXN_ERR_INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT: return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INVALID_LOADED_ACCOUNTS_DATA_SIZE_LIMIT_IDX;
+
+      case FD_RUNTIME_TXN_ERR_ACCOUNT_IN_USE:                          return FD_METRICS_ENUM_TRANSACTION_RESULT_V_ACCOUNT_IN_USE_IDX;
+      case FD_RUNTIME_TXN_ERR_ACCOUNT_LOADED_TWICE:                    return FD_METRICS_ENUM_TRANSACTION_RESULT_V_ACCOUNT_LOADED_TWICE_IDX;
+      case FD_RUNTIME_TXN_ERR_SIGNATURE_FAILURE:                       return FD_METRICS_ENUM_TRANSACTION_RESULT_V_SIGNATURE_FAILURE_IDX;
+      case FD_RUNTIME_TXN_ERR_TOO_MANY_ACCOUNT_LOCKS:                  return FD_METRICS_ENUM_TRANSACTION_RESULT_V_TOO_MANY_ACCOUNT_LOCKS_IDX;
+
+      case FD_RUNTIME_TXN_ERR_INSUFFICIENT_FUNDS_FOR_RENT:             return FD_METRICS_ENUM_TRANSACTION_RESULT_V_INSUFFICIENT_FUNDS_FOR_RENT_IDX;
+      case FD_RUNTIME_TXN_ERR_UNBALANCED_TRANSACTION:                  return FD_METRICS_ENUM_TRANSACTION_RESULT_V_UNBALANCED_TRANSACTION_IDX;
 
       case FD_RUNTIME_TXN_ERR_CALL_CHAIN_TOO_DEEP:
       case FD_RUNTIME_TXN_ERR_MISSING_SIGNATURE_FOR_FEE:
```

### src/discof/bank/fd_bank_tile.c
```diff
@@ -10,6 +10,7 @@
 #include "../../util/pod/fd_pod_format.h"
 #include "../../disco/pack/fd_pack_rebate_sum.h"
 #include "../../disco/metrics/generated/fd_metrics_bank.h"
+#include "../../disco/metrics/generated/fd_metrics_enums.h"
 #include "../../flamenco/runtime/fd_runtime.h"
 #include "../../flamenco/runtime/fd_bank.h"
 
@@ -48,7 +49,7 @@ typedef struct {
   fd_exec_txn_ctx_t txn_ctx[1];
 
   struct {
-    ulong txn_result[ 1-FD_BANK_TXN_ERR_LAST ];
+    ulong txn_result[ FD_METRICS_ENUM_TRANSACTION_RESULT_CNT ];
   } metrics;
 } fd_bank_ctx_t;
 
@@ -162,7 +163,7 @@ handle_microblock( fd_bank_ctx_t *     ctx,
 
     int err = fd_runtime_prepare_and_execute_txn( ctx->banks, ctx->_bank_idx, txn_ctx, txn, ctx->exec_spad, NULL, 0 );
     if( FD_UNLIKELY( !(txn_ctx->flags & FD_TXN_P_FLAGS_SANITIZE_SUCCESS ) ) ) {
-      ctx->metrics.txn_result[ -fd_bank_err_from_runtime_err( err ) ]++;
+      ctx->metrics.txn_result[ fd_bank_err_from_runtime_err( err ) ]++;
       continue;
     }
 
@@ -185,7 +186,7 @@ handle_microblock( fd_bank_ctx_t *     ctx,
              that pack and GUI expect ... */
     txn->flags = (txn->flags & 0x00FFFFFFU) | ((uint)(-err)<<24);
 
-    ctx->metrics.txn_result[ -fd_bank_err_from_runtime_err( err ) ]++;
+    ctx->metrics.txn_result[ fd_bank_err_from_runtime_err( err ) ]++;
 
     uint actual_execution_cus = (uint)(txn_ctx->compute_budget_details.compute_unit_limit - txn_ctx->compute_budget_details.compute_meter);
     uint actual_acct_data_cus = (uint)(txn_ctx->loaded_accounts_data_size);
@@ -338,7 +339,7 @@ handle_bundle( fd_bank_ctx_t *     ctx,
     (void)out_timestamps; // TODO: GUI, report timestamps
   }
 
-  for( ulong i=0UL; i<txn_cnt; i++ ) ctx->metrics.txn_result[ -fd_bank_err_from_runtime_err( transaction_err[ i ] ) ]++;
+  for( ulong i=0UL; i<txn_cnt; i++ ) ctx->metrics.txn_result[ fd_bank_err_from_runtime_err( transaction_err[ i ] ) ]++;
 
   if( FD_LIKELY( execution_success ) ) {
     for( ulong i=0UL; i<txn_cnt; i++ ) {
```
