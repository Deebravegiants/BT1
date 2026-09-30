# [?] Tests: Fix test node_server.bind_same_p2p_port from randomly crashing

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-04-05
Source: https://github.com/monero-project/monero/commit/176cea0ec6ca2f16f9dc9f4280a9c4513828139e
Type: security-commit

## Details
Tests: Fix test node_server.bind_same_p2p_port from randomly crashing

## Patch
### tests/unit_tests/node_server.cpp
```diff
@@ -293,6 +293,18 @@ TEST(node_server, bind_same_p2p_port)
     boost::program_options::variables_map vm;
     boost::program_options::store(boost::program_options::parse_command_line(1, argv, desc_options), vm);
 
+    /*
+    Reason for choosing '127.0.0.2' as the IP:
+
+    A TCP local socket address that has been bound is unavailable for some time after closing, unless the SO_REUSEADDR flag has been set.
+    That's why connections with automatically assigned source port 48080/58080 from previous test blocks the next to bind acceptor
+    so solution is to either set reuse_addr option for each socket in all tests
+    or use ip different from localhost for acceptors in order to not interfere with automatically assigned source endpoints
+
+    Relevant part about REUSEADDR from man:
+    https://www.man7.org/linux/man-pages/man7/ip.7.html
+    */
+    vm.find(nodetool::arg_p2p_bind_ip.name)->second   = boost::program_options::variable_value(std::string("127.0.0.2"), false);
     vm.find(nodetool::arg_p2p_bind_port.name)->second = boost::program_options::variable_value(std::string(port), false);
 
     boost::program_options::notify(vm);
```
