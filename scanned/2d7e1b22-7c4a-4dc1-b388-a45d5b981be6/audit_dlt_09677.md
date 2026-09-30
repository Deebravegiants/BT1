# [?] GH-1677 Avoid stack overflow by posting to ship io_context on recursive send()

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-10-13
Source: https://github.com/AntelopeIO/leap/commit/fa5ff2f966b3d416d410f92c3d8828395b10499f
Type: security-commit

## Details
GH-1677 Avoid stack overflow by posting to ship io_context on recursive send()

## Patch
### plugins/state_history_plugin/include/eosio/state_history_plugin/session.hpp
```diff
@@ -57,11 +57,15 @@ class session_manager {
 private:
    using entry_ptr = std::unique_ptr<send_queue_entry_base>;
 
+   boost::asio::io_context& ship_io_context;
    std::set<std::shared_ptr<session_base>> session_set;
    bool sending  = false;
    std::deque<std::pair<std::shared_ptr<session_base>, entry_ptr>> send_queue;
 
 public:
+   explicit session_manager(boost::asio::io_context& ship_io_context)
+   : ship_io_context(ship_io_context) {}
+
    void insert(std::shared_ptr<session_base> s) {
       session_set.insert(std::move(s));
    }
@@ -103,8 +107,12 @@ class session_manager {
    void pop_entry(bool call_send = true) {
       send_queue.erase(send_queue.begin());
       sending = false;
-      if (call_send || !send_queue.empty())
-         send();
+      if (call_send || !send_queue.empty()) {
+         // avoid blowing the stack
+         boost::asio::post(ship_io_context, [this]() {
+            send();
+         });
+      }
    }
 
    void send_updates() {
```

### plugins/state_history_plugin/state_history_plugin.cpp
```diff
@@ -75,7 +75,6 @@ struct state_history_plugin_impl : std::enable_shared_from_this<state_history_pl
    uint16_t                         endpoint_port = 8080;
    string                           unix_path;
    state_history::trace_converter   trace_converter;
-   session_manager                  session_mgr;
 
    mutable std::mutex mtx;
    block_id_type head_id;
@@ -101,6 +100,8 @@ struct state_history_plugin_impl : std::enable_shared_from_this<state_history_pl
 
    named_thread_pool<struct ship> thread_pool;
 
+   session_manager                  session_mgr{thread_pool.get_executor()};
+
    bool  plugin_started = false;
 
    static fc::logger& logger() { return _log; }
```

### plugins/state_history_plugin/tests/session_test.cpp
```diff
@@ -100,7 +100,7 @@ struct mock_state_history_plugin {
    fc::temp_directory                      log_dir;
    std::optional<eosio::state_history_log> log;
    std::atomic<bool>                       stopping = false;
-   eosio::session_manager                  session_mgr;
+   eosio::session_manager                  session_mgr{ship_ioc};
 
    constexpr static uint32_t default_frame_size = 1024;
 
```
