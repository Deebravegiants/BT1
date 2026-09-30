# [?] Fix potential race condition in execute_block_transactions

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2026-02-20
Source: https://github.com/category-labs/monad/commit/2f5a3ffd15ca23271eda5411eceacd265265e085
Type: security-commit

## Details
Fix potential race condition in execute_block_transactions

Use just promise to synchronize with last transaction

## Patch
### category/execution/ethereum/execute_block.cpp
```diff
@@ -232,7 +232,6 @@ Result<std::vector<Receipt>> execute_block_transactions(
 
     std::shared_ptr<std::optional<Result<Receipt>>[]> const results{
         new std::optional<Result<Receipt>>[transactions.size()]};
-    std::atomic<size_t> txn_exec_finished = 0;
     size_t const txn_count = transactions.size();
 
     auto const tx_exec_begin = std::chrono::steady_clock::now();
@@ -252,7 +251,6 @@ Result<std::vector<Receipt>> execute_block_transactions(
              &block_metrics,
              &call_tracer = *call_tracers[i],
              &state_tracer = *state_tracers[i],
-             &txn_exec_finished,
              &chain_ctx = chain_ctx] {
                 record_txn_marker_event(MONAD_EXEC_TXN_PERF_EVM_ENTER, i);
                 try {
@@ -270,16 +268,17 @@ Result<std::vector<Receipt>> execute_block_transactions(
                         call_tracer,
                         state_tracer,
                         chain_ctx);
-                    promises[i + 1].set_value();
                     if (results[i]->has_error()) {
                         record_txn_error_event(i, results[i]->error());
                     }
                     record_txn_marker_event(MONAD_EXEC_TXN_PERF_EVM_EXIT, i);
+                    // Call promise.set_value/set_exception the last thing,
+                    // because this signals that the transaction is finished.
+                    promises[i + 1].set_value();
                 }
                 catch (...) {
                     promises[i + 1].set_exception(std::current_exception());
                 }
-                txn_exec_finished.fetch_add(1, std::memory_order::relaxed);
             });
     }
 
@@ -289,15 +288,6 @@ Result<std::vector<Receipt>> execute_block_transactions(
         std::chrono::duration_cast<std::chrono::microseconds>(
             std::chrono::steady_clock::now() - tx_exec_begin);
 
-    // All transactions have released their merge-order synchronization
-    // primitive (promises[i + 1]) but some stragglers could still be running
-    // post-execution code that occurs immediately after that, e.g.
-    // `record_txn_exec_result_events`. This waits for everything to finish
-    // so that it's safe to assume we're the only ones using `results`.
-    while (txn_exec_finished.load() < txn_count) {
-        cpu_relax();
-    }
-
     std::vector<Receipt> retvals;
     for (unsigned i = 0; i < transactions.size(); ++i) {
         MONAD_ASSERT(results[i].has_value());
```
