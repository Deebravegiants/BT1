# [?] GH-1639 Fix producer_plugin shutdown of read only threads to prevent SEGFAULT and deadlock.

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-09-18
Source: https://github.com/AntelopeIO/leap/commit/6af28bb0f9a01fcb77739dc942f3b0ccfe808e5c
Type: security-commit

## Details
GH-1639 Fix producer_plugin shutdown of read only threads to prevent SEGFAULT and deadlock.

## Patch
### libraries/custom_appbase/include/eosio/chain/application.hpp
```diff
@@ -79,6 +79,12 @@ class two_queue_executor {
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
@@ -13,6 +13,12 @@ class exec_pri_queue : public boost::asio::execution_context
 {
 public:
 
+   void stop() {
+      std::lock_guard g( mtx_ );
+      exiting_blocking_ = true;
+      cond_.notify_all();
+   }
+
    void enable_locking(uint32_t num_threads, std::function<bool()> should_exit) {
       assert(num_threads > 0 && num_waiting_ == 0);
       lock_enabled_ = true;
```

### plugins/producer_plugin/producer_plugin.cpp
```diff
@@ -1389,20 +1389,13 @@ void producer_plugin::plugin_startup()
 } FC_CAPTURE_AND_RETHROW() }
 
 void producer_plugin::plugin_shutdown() {
-   try {
-      my->_timer.cancel();
-   } catch ( const std::bad_alloc& ) {
-     chain_plugin::handle_bad_alloc();
-   } catch ( const boost::interprocess::bad_alloc& ) {
-     chain_plugin::handle_bad_alloc();
-   } catch(const fc::exception& e) {
-      edump((e.to_detail_string()));
-   } catch(const std::exception& e) {
-      edump((fc::std_exception_wrapper::from_current_exception(e).to_detail_string()));
-   }
-
+   boost::system::error_code ec;
+   my->_timer.cancel(ec);
+   boost::system::error_code ro_ec;
+   my->_ro_timer.cancel(ro_ec);
+   app().executor().stop();
+   my->_ro_thread_pool.stop();
    my->_thread_pool.stop();
-
    my->_unapplied_transactions.clear();
 
    app().executor().post( 0, [me = my](){} ); // keep my pointer alive until queue is drained
```
