# [?] async_protocol_handler_config: fix deadlock

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-03-12
Source: https://github.com/monero-project/monero/commit/2935a0c47909cf964141a1feee5cd3c4721c2826
Type: security-commit

## Details
async_protocol_handler_config: fix deadlock

## Patch
### contrib/epee/include/net/levin_protocol_handler_async.h
```diff
@@ -769,36 +769,32 @@ void async_protocol_handler_config<t_connection_context>::del_connection(async_p
 template<class t_connection_context>
 void async_protocol_handler_config<t_connection_context>::delete_connections(size_t count, bool incoming)
 {
-  std::vector <boost::uuids::uuid> connections;
+  std::vector<typename connections_map::mapped_type> connections;
+
+  auto scope_exit_handler = misc_utils::create_scope_leave_handler([&connections]{
+    for (auto &aph: connections)
+      aph->finish_outer_call();
+  });
+
   CRITICAL_REGION_BEGIN(m_connects_lock);
   for (auto& c: m_connects)
   {
     if (c.second->m_connection_context.m_is_income == incoming)
-      connections.push_back(c.first);
+      if (c.second->start_outer_call())
+        connections.push_back(c.second);
   }
 
   // close random connections from  the provided set
   // TODO or better just keep removing random elements (performance)
   unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
   shuffle(connections.begin(), connections.end(), std::default_random_engine(seed));
-  while (count > 0 && connections.size() > 0)
-  {
-    try
-    {
-      auto i = connections.end() - 1;
-      async_protocol_handler<t_connection_context> *conn = m_connects.at(*i);
-      m_connects.erase(*i);
-      conn->close();
-      connections.erase(i);
-    }
-    catch (const std::out_of_range &e)
-    {
-      MWARNING("Connection not found in m_connects, continuing");
-    }
-    --count;
-  }
+  for (size_t i = 0; i < connections.size() && i < count; ++i)
+    m_connects.erase(connections[i]->get_connection_id());
 
   CRITICAL_REGION_END();
+
+  for (size_t i = 0; i < connections.size() && i < count; ++i)
+    connections[i]->close();
 }
 //------------------------------------------------------------------------------------------
 template<class t_connection_context>
@@ -860,18 +856,19 @@ int async_protocol_handler_config<t_connection_context>::invoke_async(int comman
 template<class t_connection_context> template<class callback_t>
 bool async_protocol_handler_config<t_connection_context>::foreach_connection(const callback_t &cb)
 {
-  CRITICAL_REGION_LOCAL(m_connects_lock);
   std::vector<typename connections_map::mapped_type> conn;
-  conn.reserve(m_connects.size());
 
   auto scope_exit_handler = misc_utils::create_scope_leave_handler([&conn]{
     for (auto &aph: conn)
       aph->finish_outer_call();
   });
 
+  CRITICAL_REGION_BEGIN(m_connects_lock);
+  conn.reserve(m_connects.size());
   for (auto &e: m_connects)
     if (e.second->start_outer_call())
       conn.push_back(e.second);
+  CRITICAL_REGION_END()
 
   for (auto &aph: conn)
     if (!cb(aph->get_context_ref()))
@@ -883,11 +880,8 @@ bool async_protocol_handler_config<t_connection_context>::foreach_connection(con
 template<class t_connection_context> template<class callback_t>
 bool async_protocol_handler_config<t_connection_context>::for_connection(const boost::uuids::uuid &connection_id, const callback_t &cb)
 {
-  CRITICAL_REGION_LOCAL(m_connects_lock);
-  async_protocol_handler<t_connection_context>* aph = find_connection(connection_id);
-  if (!aph)
-    return false;
-  if (!aph->start_outer_call())
+  async_protocol_handler<t_connection_context>* aph = nullptr;
+  if (find_and_lock_connection(connection_id, aph) != LEVIN_OK)
     return false;
   auto scope_exit_handler = misc_utils::create_scope_leave_handler(
     boost::bind(&async_protocol_handler<t_connection_context>::finish_outer_call, aph));
@@ -953,12 +947,14 @@ int async_protocol_handler_config<t_connection_context>::send(byte_slice message
 template<class t_connection_context>
 bool async_protocol_handler_config<t_connection_context>::close(boost::uuids::uuid connection_id)
 {
-  CRITICAL_REGION_LOCAL(m_connects_lock);
-  async_protocol_handler<t_connection_context>* aph = find_connection(connection_id);
-  if (!aph)
+  async_protocol_handler<t_connection_context>* aph = nullptr;
+  if (find_and_lock_connection(connection_id, aph) != LEVIN_OK)
     return false;
+  auto scope_exit_handler = misc_utils::create_scope_leave_handler(
+    boost::bind(&async_protocol_handler<t_connection_context>::finish_outer_call, aph));
   if (!aph->close())
     return false;
+  CRITICAL_REGION_LOCAL(m_connects_lock);
   m_connects.erase(connection_id);
   return true;
 }
```
