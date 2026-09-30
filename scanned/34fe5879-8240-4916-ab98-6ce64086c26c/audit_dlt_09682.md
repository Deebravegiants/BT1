# [?] fix crash caused by handle_push_result

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-03-09
Source: https://github.com/AntelopeIO/leap/commit/832fa96e096024671bc985e4ff832caee3271bf7
Type: security-commit

## Details
fix crash caused by handle_push_result

## Patch
### plugins/producer_plugin/producer_plugin.cpp
```diff
@@ -298,11 +298,11 @@ class producer_plugin_impl : public std::enable_shared_from_this<producer_plugin
                                       const fc::time_point& start,
                                       const chain::controller& chain,
                                       const transaction_trace_ptr& trace,
-                                      bool return_failure_trace = true,
-                                      bool disable_subjective_enforcement = false,
-                                      account_name first_auth = {},
-                                      int64_t sub_bill = 0,
-                                      uint32_t prev_billed_cpu_time_us = 0);
+                                      bool return_failure_trace,
+                                      bool disable_subjective_enforcement,
+                                      account_name first_auth,
+                                      int64_t sub_bill,
+                                      uint32_t prev_billed_cpu_time_us );
       void log_trx_results( const transaction_metadata_ptr& trx, const transaction_trace_ptr& trace, const fc::time_point& start );
       void log_trx_results( const transaction_metadata_ptr& trx, const fc::exception_ptr& except_ptr );
       void log_trx_results( const packed_transaction_ptr& trx, const transaction_trace_ptr& trace,
@@ -2168,7 +2168,8 @@ producer_plugin_impl::handle_push_result( const transaction_metadata_ptr& trx,
    auto end = fc::time_point::now();
    push_result pr;
    if( trace->except ) {
-      _account_fails.add_fail_time(end - start);
+      if ( !trx->is_read_only() )
+         _account_fails.add_fail_time(end - start);
       if( exception_is_exhausted( *trace->except ) ) {
          if( _pending_block_mode == pending_block_mode::producing ) {
             fc_dlog(_trx_failed_trace_log, "[TRX_TRACE] Block ${block_num} for producer ${prod} COULD NOT FIT, tx: ${txid} RETRYING ",
@@ -2207,7 +2208,8 @@ producer_plugin_impl::handle_push_result( const transaction_metadata_ptr& trx,
    } else {
       fc_tlog( _log, "Subjective bill for success ${a}: ${b} elapsed ${t}us, time ${r}us",
                ("a",first_auth)("b",sub_bill)("t",trace->elapsed)("r", end - start));
-      _account_fails.add_success_time(end - start);
+      if ( !trx->is_read_only() )
+         _account_fails.add_success_time(end - start);
       log_trx_results( trx, trace, start );
       // if producing then trx is in objective cpu account billing
       if (!disable_subjective_enforcement && _pending_block_mode != pending_block_mode::producing) {
@@ -2828,7 +2830,7 @@ bool producer_plugin_impl::push_read_only_transaction(
       auto available_trx_time_us = std::min( remained_time_in_read_window_us, _ro_max_trx_time_us );
 
       auto trace = chain.push_transaction( trx, block_deadline, available_trx_time_us, 0, false, 0 );
-      auto pr = handle_push_result(trx, next, start, chain, trace);
+      auto pr = handle_push_result(trx, next, start, chain, trace, true /*return_failure_trace*/, true /*disable_subjective_enforcement*/, {} /*first_auth*/, 0 /*sub_bill*/, 0 /*prev_billed_cpu_time_us*/);
       // If a transaction or block was exhausted, that indicates we are close to
       // the end of read window or block boundary. Retry in next round.
       retry = pr.block_exhausted || pr.trx_exhausted;
```
