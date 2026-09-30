# [?] abstract_tcp_server2: fix crashy race on socket shutdown

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-03-13
Source: https://github.com/monero-project/monero/commit/1659029469179bd4f07c6a5ea6cbab6053597793
Type: security-commit

## Details
abstract_tcp_server2: fix crashy race on socket shutdown

## Patch
### contrib/epee/include/net/abstract_tcp_server2.inl
```diff
@@ -670,9 +670,9 @@ PRAGMA_WARNING_DISABLE_VS(4355)
         CHECK_AND_ASSERT_MES( size_now == m_send_que.front().size(), false, "Unexpected queue size");
         reset_timer(get_default_timeout(), false);
             async_write(boost::asio::buffer(m_send_que.front().data(), size_now ) ,
-                                 //strand_.wrap(
+                                 strand_.wrap(
                                  boost::bind(&connection<t_protocol_handler>::handle_write, self, _1, _2)
-                                 //)
+                                 )
                                  );
         //_dbg3("(chunk): " << size_now);
         //logger_handle_net_write(size_now);
@@ -761,8 +761,9 @@ PRAGMA_WARNING_DISABLE_VS(4355)
     // Initiate graceful connection closure.
     m_timer.cancel();
     boost::system::error_code ignored_ec;
+    if (m_ssl_support == epee::net_utils::ssl_support_t::e_ssl_support_enabled)
+      socket_.shutdown(ignored_ec);
     socket().shutdown(boost::asio::ip::tcp::socket::shutdown_both, ignored_ec);
-    socket().close();
     if (!m_host.empty())
     {
       try { host_count(m_host, -1); } catch (...) { /* ignore */ }
@@ -855,9 +856,9 @@ PRAGMA_WARNING_DISABLE_VS(4355)
 			do_send_handler_write_from_queue(e, m_send_que.front().size() , m_send_que.size()); // (((H)))
 		CHECK_AND_ASSERT_MES( size_now == m_send_que.front().size(), void(), "Unexpected queue size");
 		  async_write(boost::asio::buffer(m_send_que.front().data(), size_now) , 
-          // strand_.wrap(
+           strand_.wrap(
             boost::bind(&connection<t_protocol_handler>::handle_write, connection<t_protocol_handler>::shared_from_this(), _1, _2)
-				  // )
+			  )
           );
       //_dbg3("(normal)" << size_now);
     }
```
