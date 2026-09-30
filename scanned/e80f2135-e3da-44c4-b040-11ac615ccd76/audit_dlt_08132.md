# [?] cryptonote_protocol_handler: fix race condition

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-03-22
Source: https://github.com/monero-project/monero/commit/fe632560f42150e31c868db9dd6b2649a0170651
Type: security-commit

## Details
cryptonote_protocol_handler: fix race condition

## Patch
### src/cryptonote_basic/connection_context.h
```diff
@@ -77,6 +77,8 @@ namespace cryptonote
     int m_expect_response;
     uint64_t m_expect_height;
     size_t m_num_requested;
+    epee::copyable_atomic m_new_stripe_notification{0};
+    epee::copyable_atomic m_idle_peer_notification{0};
   };
 
   inline std::string get_protocol_state_string(cryptonote_connection_context::state s)
```

### src/cryptonote_protocol/cryptonote_protocol_handler.inl
```diff
@@ -137,6 +137,41 @@ namespace cryptonote
     CHECK_AND_ASSERT_MES_CC( context.m_callback_request_count > 0, false, "false callback fired, but context.m_callback_request_count=" << context.m_callback_request_count);
     --context.m_callback_request_count;
 
+    uint32_t notified = true;
+    if (context.m_idle_peer_notification.compare_exchange_strong(notified, not notified))
+    {
+      if (context.m_state == cryptonote_connection_context::state_synchronizing && context.m_last_request_time != boost::date_time::not_a_date_time)
+      {
+        const boost::posix_time::ptime now = boost::posix_time::microsec_clock::universal_time();
+        const boost::posix_time::time_duration dt = now - context.m_last_request_time;
+        const auto ms = dt.total_microseconds();
+        if (ms > IDLE_PEER_KICK_TIME || (context.m_expect_response && ms > NON_RESPONSIVE_PEER_KICK_TIME))
+        {
+          if (context.m_score-- >= 0)
+          {
+            MINFO(context << " kicking idle peer, last update " << (dt.total_microseconds() / 1.e6) << " seconds ago, expecting " << (int)context.m_expect_response);
+            context.m_last_request_time = boost::date_time::not_a_date_time;
+            context.m_expect_response = 0;
+            context.m_expect_height = 0;
+            context.m_state = cryptonote_connection_context::state_standby; // we'll go back to adding, then (if we can't), download
+          }
+          else
+          {
+            MINFO(context << "dropping idle peer with negative score");
+            drop_connection_with_score(context, context.m_expect_response == 0 ? 1 : 5, false);
+            return false;
+          }
+        }
+      }
+    }
+
+    notified = true;
+    if (context.m_new_stripe_notification.compare_exchange_strong(notified, not notified))
+    {
+      if (context.m_state == cryptonote_connection_context::state_normal)
+        context.m_state = cryptonote_connection_context::state_synchronizing;
+    }
+
     if(context.m_state == cryptonote_connection_context::state_synchronizing && context.m_last_request_time == boost::posix_time::not_a_date_time)
     {
       NOTIFY_REQUEST_CHAIN::request r = {};
@@ -1687,7 +1722,7 @@ skip:
         const uint32_t peer_stripe = tools::get_pruning_stripe(context.m_pruning_seed);
         if (stripe && peer_stripe && peer_stripe != stripe)
           return true;
-        context.m_state = cryptonote_connection_context::state_synchronizing;
+        context.m_new_stripe_notification = true;
         LOG_PRINT_CCONTEXT_L2("requesting callback");
         ++context.m_callback_request_count;
         m_p2p->request_callback(context);
@@ -1710,7 +1745,6 @@ skip:
   bool t_cryptonote_protocol_handler<t_core>::kick_idle_peers()
   {
     MTRACE("Checking for idle peers...");
-    std::vector<std::pair<boost::uuids::uuid, unsigned>> idle_peers;
     m_p2p->for_each_connection([&](cryptonote_connection_context& context, nodetool::peerid_type peer_id, uint32_t support_flags)->bool
     {
       if (context.m_state == cryptonote_connection_context::state_synchronizing && context.m_last_request_time != boost::date_time::not_a_date_time)
@@ -1720,36 +1754,16 @@ skip:
         const auto ms = dt.total_microseconds();
         if (ms > IDLE_PEER_KICK_TIME || (context.m_expect_response && ms > NON_RESPONSIVE_PEER_KICK_TIME))
         {
-          if (context.m_score-- >= 0)
-          {
-            MINFO(context << " kicking idle peer, last update " << (dt.total_microseconds() / 1.e6) << " seconds ago, expecting " << (int)context.m_expect_response);
-            LOG_PRINT_CCONTEXT_L2("requesting callback");
-            context.m_last_request_time = boost::date_time::not_a_date_time;
-            context.m_expect_response = 0;
-            context.m_expect_height = 0;
-            context.m_state = cryptonote_connection_context::state_standby; // we'll go back to adding, then (if we can't), download
-            ++context.m_callback_request_count;
-            m_p2p->request_callback(context);
-          }
-          else
-          {
-            idle_peers.push_back(std::make_pair(context.m_connection_id, context.m_expect_response == 0 ? 1 : 5));
-          }
+          context.m_idle_peer_notification = true;
+          LOG_PRINT_CCONTEXT_L2("requesting callback");
+          ++context.m_callback_request_count;
+          m_p2p->request_callback(context);
+          MLOG_PEER_STATE("requesting callback");
         }
       }
       return true;
     });
 
-    for (const auto &e: idle_peers)
-    {
-      const auto &uuid = e.first;
-      m_p2p->for_connection(uuid, [&](cryptonote_connection_context& ctx, nodetool::peerid_type peer_id, uint32_t f)->bool{
-        MINFO(ctx << "dropping idle peer with negative score");
-        drop_connection_with_score(ctx, e.second, false);
-        return true;
-      });
-    }
-
     return true;
   }
   //------------------------------------------------------------------------------------------------------------------------
```
