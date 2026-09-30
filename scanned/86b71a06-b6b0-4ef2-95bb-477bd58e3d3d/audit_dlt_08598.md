# [?] Fix websocket deadlock:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2016-01-14
Source: https://github.com/XRPLF/rippled/commit/07c4262392bffa31b199c2de3d6b7ef62c93a58f
Type: security-commit

## Details
Fix websocket deadlock:

A copy of the connection list is made on stop so it
can be iterated without holding the endpoint lock.

## Patch
### src/websocketpp_02/src/endpoint.hpp
```diff
@@ -334,18 +334,23 @@ class endpoint
     void close_all(close::status::value code = close::status::GOING_AWAY,
                    const std::string& reason = "")
     {
-        boost::lock_guard<boost::recursive_mutex> lock(m_lock);
+        auto connections = [&, this]
+        {
+            boost::lock_guard<boost::recursive_mutex> lock (m_lock);
 
-        m_alog->at(log::alevel::ENDPOINT)
-        << "Endpoint received signal to close all connections cleanly with code "
-        << code << " and reason " << reason << log::endl;
+            m_alog->at (log::alevel::ENDPOINT)
+                << "Endpoint received signal to close all connections cleanly "
+                   "with code "
+                << code << " and reason " << reason << log::endl;
+            return m_connections;
+        }();
 
         // TODO: is there a more elegant way to do this? In some code paths
         // close can call terminate immediately which removes the connection
         // from m_connections, invalidating the iterator.
         typename std::set<connection_ptr>::iterator it;
 
-        for (it = m_connections.begin(); it != m_connections.end();) {
+        for (it = connections.begin(); it != connections.end();) {
             const connection_ptr con = *it++;
             con->close(code,reason);
         }
@@ -378,15 +383,18 @@ class endpoint
               close::status::value code = close::status::GOING_AWAY,
               const std::string& reason = "")
     {
-        boost::lock_guard<boost::recursive_mutex> lock(m_lock);
 
         if (clean) {
-            m_alog->at(log::alevel::ENDPOINT)
-                << "Endpoint is stopping cleanly" << log::endl;
+            {
+                boost::lock_guard<boost::recursive_mutex> lock(m_lock);
+                m_alog->at(log::alevel::ENDPOINT)
+                        << "Endpoint is stopping cleanly" << log::endl;
 
-            m_state = STOPPING;
+                m_state = STOPPING;
+            }
             close_all(code,reason);
         } else {
+            boost::lock_guard<boost::recursive_mutex> lock(m_lock);
             m_alog->at(log::alevel::ENDPOINT)
                 << "Endpoint is stopping immediately" << log::endl;
 
```
