# [?] unit_tests: fix use after free

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-10-30
Source: https://github.com/monero-project/monero/commit/5ae02988184bc8e837830d1320b51c8577c12c91
Type: security-commit

## Details
unit_tests: fix use after free

## Patch
### tests/unit_tests/node_server.cpp
```diff
@@ -262,16 +262,25 @@ TEST(ban, ignores_port)
 
 TEST(node_server, bind_same_p2p_port)
 {
-  const auto new_node = []() -> std::unique_ptr<Server> {
+  struct test_data_t
+  {
     test_core pr_core;
-    cryptonote::t_cryptonote_protocol_handler<test_core> cprotocol(pr_core, NULL);
-    std::unique_ptr<Server> server(new Server(cprotocol));
-    cprotocol.set_p2p_endpoint(server.get());
+    cryptonote::t_cryptonote_protocol_handler<test_core> cprotocol;
+    std::unique_ptr<Server> server;
+
+    test_data_t(): cprotocol(pr_core, NULL)
+    {
+      server.reset(new Server(cprotocol));
+      cprotocol.set_p2p_endpoint(server.get());
+    }
+  };
 
-    return server;
+  const auto new_node = []() -> std::unique_ptr<test_data_t> {
+    test_data_t *d = new test_data_t;
+    return std::unique_ptr<test_data_t>(d);
   };
 
-  const auto init = [](const std::unique_ptr<Server>& server, const char* port) -> bool {
+  const auto init = [](const std::unique_ptr<test_data_t>& server, const char* port) -> bool {
     boost::program_options::options_description desc_options("Command line options");
     cryptonote::core::init_options(desc_options);
     Server::init_options(desc_options);
@@ -284,7 +293,7 @@ TEST(node_server, bind_same_p2p_port)
 
     boost::program_options::notify(vm);
 
-    return server->init(vm);
+    return server->server->init(vm);
   };
 
   constexpr char port[] = "48080";
```
