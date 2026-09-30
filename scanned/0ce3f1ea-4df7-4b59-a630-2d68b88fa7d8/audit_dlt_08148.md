# [?] p2p: fix integer overflow in host bans

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-04-11
Source: https://github.com/monero-project/monero/commit/5858598604c511ff57a434196d27acf2f49cf23f
Type: security-commit

## Details
p2p: fix integer overflow in host bans

## Patch
### src/p2p/net_node.inl
```diff
@@ -176,8 +176,15 @@ namespace nodetool
     if(!addr.is_blockable())
       return false;
 
+    const time_t now = time(nullptr);
+
     CRITICAL_REGION_LOCAL(m_blocked_hosts_lock);
-    m_blocked_hosts[addr.host_str()] = time(nullptr) + seconds;
+    time_t limit;
+    if (now > std::numeric_limits<time_t>::max() - seconds)
+      limit = std::numeric_limits<time_t>::max();
+    else
+      limit = now + seconds;
+    m_blocked_hosts[addr.host_str()] = limit;
 
     // drop any connection to that address. This should only have to look into
     // the zone related to the connection, but really make sure everything is
```

### tests/unit_tests/ban.cpp
```diff
@@ -93,18 +93,7 @@ typedef nodetool::node_server<cryptonote::t_cryptonote_protocol_handler<test_cor
 
 static bool is_blocked(Server &server, const epee::net_utils::network_address &address, time_t *t = NULL)
 {
-  const std::string host = address.host_str();
-  std::map<std::string, time_t> hosts = server.get_blocked_hosts();
-  for (auto rec: hosts)
-  {
-    if (rec.first == host)
-    {
-      if (t)
-        *t = rec.second;
-      return true;
-    }
-  }
-  return false;
+  return server.is_host_blocked(address.host_str(), t);
 }
 
 TEST(ban, add)
@@ -192,5 +181,21 @@ TEST(ban, add)
   ASSERT_TRUE(t >= 4);
 }
 
+TEST(ban, limit)
+{
+  test_core pr_core;
+  cryptonote::t_cryptonote_protocol_handler<test_core> cprotocol(pr_core, NULL);
+  Server server(cprotocol);
+  cprotocol.set_p2p_endpoint(&server);
+
+  // starts empty
+  ASSERT_TRUE(server.get_blocked_hosts().empty());
+  ASSERT_FALSE(is_blocked(server,MAKE_IPV4_ADDRESS(1,2,3,4)));
+  ASSERT_TRUE(server.block_host(MAKE_IPV4_ADDRESS(1,2,3,4), std::numeric_limits<time_t>::max() - 1));
+  ASSERT_TRUE(is_blocked(server,MAKE_IPV4_ADDRESS(1,2,3,4)));
+  ASSERT_TRUE(server.block_host(MAKE_IPV4_ADDRESS(1,2,3,4), 1));
+  ASSERT_TRUE(is_blocked(server,MAKE_IPV4_ADDRESS(1,2,3,4)));
+}
+
 namespace nodetool { template class node_server<cryptonote::t_cryptonote_protocol_handler<test_core>>; }
 namespace cryptonote { template class t_cryptonote_protocol_handler<test_core>; }
```
