# [?] Fixing a small race condition and merging functions.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-04-01
Source: https://github.com/nanocurrency/nano-node/commit/c5c4844fe33ea59bc43e71d68dbcfd4962df3b1a
Type: security-commit

## Details
Fixing a small race condition and merging functions.

## Patch
### rai/node/node.cpp
```diff
@@ -2356,13 +2356,31 @@ void rai::network::initiate_send ()
 	socket.async_send_to (boost::asio::buffer (front.data, front.size), front.endpoint, [this, front] (boost::system::error_code const & ec, size_t size_a)
 	{
 		rai::send_info self;
+		bool empty;
 		{
 			std::unique_lock <std::mutex> lock (socket_mutex);
 			assert (!sends.empty ());
 			self = sends.front ();
+			sends.pop ();
+			empty = sends.empty ();
 		}
 		self.callback (ec, size_a);
-		send_complete (ec, size_a);
+		if (node.config.logging.network_packet_logging ())
+		{
+			BOOST_LOG (node.log) << "Packet send complete";
+		}
+		if (!empty)
+		{
+			if (node.config.logging.network_packet_logging ())
+			{
+				BOOST_LOG (node.log) << boost::str (boost::format ("Delaying next packet send %1% microseconds") % node.config.packet_delay_microseconds);
+			}
+			node.alarm.add (std::chrono::system_clock::now () + std::chrono::microseconds (node.config.packet_delay_microseconds), [this] ()
+			{
+				std::unique_lock <std::mutex> lock (socket_mutex);
+				initiate_send ();
+			});
+		}
 	});
 }
 
@@ -2377,29 +2395,6 @@ void rai::network::send_buffer (uint8_t const * data_a, size_t size_a, rai::endp
 	}
 }
 
-void rai::network::send_complete (boost::system::error_code const & ec, size_t size_a)
-{
-    if (node.config.logging.network_packet_logging ())
-    {
-        BOOST_LOG (node.log) << "Packet send complete";
-    }
-	std::unique_lock <std::mutex> lock (socket_mutex);
-	assert (!sends.empty ());
-	sends.pop ();
-	if (!sends.empty ())
-	{
-		if (node.config.logging.network_packet_logging ())
-		{
-			BOOST_LOG (node.log) << boost::str (boost::format ("Delaying next packet send %1% microseconds") % node.config.packet_delay_microseconds);
-		}
-		node.alarm.add (std::chrono::system_clock::now () + std::chrono::microseconds (node.config.packet_delay_microseconds), [this] ()
-		{
-			std::unique_lock <std::mutex> lock (socket_mutex);
-			initiate_send ();
-		});
-	}
-}
-
 uint64_t rai::block_store::now ()
 {
     boost::posix_time::ptime epoch (boost::gregorian::date (1970, 1, 1));
```

### rai/node/node.hpp
```diff
@@ -279,7 +279,6 @@ class network
     void send_confirm_req (rai::endpoint const &, rai::block const &);
 	void initiate_send ();
     void send_buffer (uint8_t const *, size_t, rai::endpoint const &, std::function <void (boost::system::error_code const &, size_t)>);
-    void send_complete (boost::system::error_code const &, size_t);
     rai::endpoint endpoint ();
     rai::endpoint remote;
     std::array <uint8_t, 512> buffer;
```
