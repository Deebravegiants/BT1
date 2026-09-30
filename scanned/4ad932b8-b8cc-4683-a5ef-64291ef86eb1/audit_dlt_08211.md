# [?] Fix panic in record() (#31978)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-06-07
Source: https://github.com/solana-labs/solana/commit/ce1685f80c5e6217107647a5bd305234b3063ddd
Type: security-commit

## Details
Fix panic in record() (#31978)

## Patch
### poh/src/poh_recorder.rs
```diff
@@ -183,6 +183,13 @@ impl TransactionRecorder {
                         starting_transaction_index: None,
                     };
                 }
+                Err(PohRecorderError::SendError(e)) => {
+                    return RecordTransactionsSummary {
+                        record_transactions_timings,
+                        result: Err(PohRecorderError::SendError(e)),
+                        starting_transaction_index: None,
+                    };
+                }
                 Err(e) => panic!("Poh recorder returned unexpected error: {e:?}"),
             }
         }
```
