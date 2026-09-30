# [?] GH-1639 Fix producer_plugin shutdown of read only threads to prevent SEGFAULT and deadlock.

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-09-18
Source: https://github.com/AntelopeIO/leap/commit/1368ecd0b72f1387f0545c6deef9bd494b1aa7fe
Type: security-commit

## Details
GH-1639 Fix producer_plugin shutdown of read only threads to prevent SEGFAULT and deadlock.

## Patch
### libraries/custom_appbase/include/eosio/chain/application.hpp
```diff
@@ -119,6 +119,12 @@ class three_queue_executor {
       else
          return read_only_queue_.wrap( priority, --order_, std::forward<Function>( func));
    }
+
+   void stop() {
+      read_only_queue_.stop();
+      read_write_queue_.stop();
+      read_exclusive_queue_.stop();
+   }
      
    void clear() {
       read_only_queue_.clear();
```

### libraries/custom_appbase/include/eosio/chain/exec_pri_queue.hpp
```diff
@@ -14,7 +14,8 @@ class exec_pri_queue : public boost::asio::execution_context
 {
 public:
 
-   ~exec_pri_queue() {
+   void stop() {
+      std::lock_guard g( mtx_ );
       exiting_blocking_ = true;
       cond_.notify_all();
    }
```

### plugins/producer_plugin/producer_plugin.cpp
```diff
@@ -1427,6 +1427,10 @@ void producer_plugin::plugin_startup() {
 void producer_plugin_impl::plugin_shutdown() {
    boost::system::error_code ec;
    _timer.cancel(ec);
+   boost::system::error_code ro_ec;
+   _ro_timer.cancel(ro_ec);
+   app().executor().stop();
+   _ro_thread_pool.stop();
    _thread_pool.stop();
    _unapplied_transactions.clear();
 
```
