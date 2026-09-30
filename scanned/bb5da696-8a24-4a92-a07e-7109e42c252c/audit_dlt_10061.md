# [?] Merge pull request #5090 from clemahieu/asc_pull-dos-fix

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-06-29
Source: https://github.com/nanocurrency/nano-node/commit/a945ab419dbb7c504b2a69021116290186f7a8b9
Type: security-commit

## Details
Merge pull request #5090 from clemahieu/asc_pull-dos-fix

Restore oversized read buffer

## Patch
### .gitignore
```diff
@@ -18,6 +18,9 @@
 # Doxygen built HTML
 /doc-build
 
+# CMake build directory (default location used by ci/build.sh)
+/build/
+
 # Executables
 *.exe
 *.out
```

### nano/core_test/tcp_listener.cpp
```diff
@@ -1,7 +1,9 @@
 #include <nano/boost/asio/ip/address_v6.hpp>
 #include <nano/boost/asio/ip/network_v6.hpp>
+#include <nano/lib/stream.hpp>
 #include <nano/lib/thread_runner.hpp>
 #include <nano/messages/keepalive.hpp>
+#include <nano/messages/message_header.hpp>
 #include <nano/messages/message_type.hpp>
 #include <nano/messages/node_id_handshake.hpp>
 #include <nano/node/network.hpp>
@@ -242,4 +244,36 @@ TEST (tcp_listener, timeout_node_id_handshake)
 	ASSERT_TIMELY (5s, node0->stats.count (nano::stat::type::tcp_server, nano::stat::detail::node_id_handshake) != 0);
 	ASSERT_TIMELY_EQ (5s, node0->tcp_listener.connection_count (), 1);
 	ASSERT_TIMELY_EQ (10s, node0->tcp_listener.connection_count (), 0);
-}
\ No newline at end of file
+}
+
+// A header declaring the maximum payload its length field can encode must not crash the node.
+TEST (tcp_listener, asc_pull_oversized_payload_no_crash)
+{
+	nano::test::system system;
+	nano::node_config config;
+	config.tcp->handshake_timeout = 2s;
+	auto node = system.add_node (config);
+
+	nano::messages::message_header header{ nano::dev::network_params.network, nano::messages::message_type::asc_pull_req };
+	header.extensions = nano::messages::message_header::extensions_bitset_t{ 0xffff };
+
+	auto bytes = std::make_shared<std::vector<uint8_t>> ();
+	{
+		nano::vectorstream stream{ *bytes };
+		header.serialize (stream);
+	}
+
+	auto socket = std::make_shared<nano::transport::tcp_socket> (*node);
+	std::atomic<bool> write_done{ false };
+	socket->async_connect (node->tcp_listener.endpoint (), [socket, bytes, &write_done] (boost::system::error_code const & ec) {
+		ASSERT_FALSE (ec);
+		socket->async_write (bytes, [&write_done] (boost::system::error_code const & ec, size_t size) {
+			ASSERT_FALSE (ec);
+			write_done = true;
+		});
+	});
+	ASSERT_TIMELY (5s, write_done);
+
+	// The header fits the buffer, so the node reads it and stalls on the absent body until timeout.
+	ASSERT_TIMELY_EQ (10s, node->tcp_listener.connection_count (), 0);
+}
```

### nano/node/transport/tcp_server.cpp
```diff
@@ -11,6 +11,7 @@
 #include <nano/node/transport/tcp_listener.hpp>
 #include <nano/node/transport/tcp_server.hpp>
 
+#include <limits>
 #include <memory>
 
 nano::transport::tcp_server::tcp_server (nano::node & node_a, std::shared_ptr<nano::transport::tcp_socket> socket_a) :
@@ -20,6 +21,7 @@ nano::transport::tcp_server::tcp_server (nano::node & node_a, std::shared_ptr<na
 	task{ strand },
 	buffer{ std::make_shared<nano::shared_buffer::element_type> (max_buffer_size) }
 {
+	static_assert (max_buffer_size >= nano::messages::asc_pull_req::partial_size + std::numeric_limits<uint16_t>::max (), "buffer must hold the largest payload a header length field can request");
 }
 
 nano::transport::tcp_server::~tcp_server ()
@@ -277,6 +279,12 @@ auto nano::transport::tcp_server::receive_message_impl () -> asio::awaitable<nan
 
 	auto const payload_size = header.payload_length_bytes ();
 
+	// Declared length is untrusted; never let it drive a read past the buffer.
+	if (payload_size > max_buffer_size)
+	{
+		co_return nano::deserialize_message_result{ nullptr, nano::deserialize_message_status::invalid_header };
+	}
+
 	node.stats.inc (nano::stat::type::tcp_server, nano::stat::detail::read_payload, nano::stat::dir::in);
 	node.stats.inc (nano::stat::type::tcp_server_read, to_stat_detail (header.type), nano::stat::dir::in);
 
```

### nano/node/transport/tcp_server.hpp
```diff
@@ -70,7 +70,8 @@ class tcp_server final : public std::enable_shared_from_this<tcp_server>
 	nano::async::task task;
 
 	nano::shared_buffer buffer;
-	static size_t constexpr max_buffer_size = 64 * 1024; // 64 KB
+	// Larger than any payload a header length field can request, so a read can never exceed it.
+	static size_t constexpr max_buffer_size = 65 * 1024;
 
 	std::atomic<bool> handshake_received{ false };
 
```
