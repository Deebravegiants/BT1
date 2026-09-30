# [?] Fix use-after-free in rpc test response helper (#5166)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-09-10
Source: https://github.com/nanocurrency/nano-node/commit/a1ccec51a113f95e8adedff9595c7acc6e11364b
Type: security-commit

## Details
Fix use-after-free in rpc test response helper (#5166)

* Fix use-after-free in rpc test response helper

`test_response` chained async_connect -> async_write -> async_read with handlers
capturing a raw `this`, while callers held it by value or unique_ptr. Nothing tied
the object's lifetime to the operations it had started, so dropping the caller's
handle mid-flight left queued handlers pointing at freed memory. A failing
ASSERT_TIMELY inside `wait_response_impl` is exactly that path, since it expands
to a bare `return`.

The macOS TSAN CI job hits this as a SEGV during `~system()`: the RPC request times
out, the stack allocated `test_response` is destroyed, and the pending write
completion then starts a read on the destroyed socket while the teardown poll loop
drains the io_context.

Make `test_response` shared and give every handler a lifetime guard. Construction
goes through `prepare`/`send`, so stack allocating one - the shape that caused the
bug - no longer compiles. `request` becomes a value copy, as the object can now
legitimately outlive the caller's ptree.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

* Join worker threads in rpc simultaneous_calls

The worker threads were detached while capturing `test_responses`, `promise` and
`count` by reference. A failing assertion returns from the test body and destroys
those stack objects, so any assertion firing while the threads are still running
left them writing into dead memory - the same defect as the response helper, one
scope up. Injecting an early assertion failure and running under ASAN reports
`stack-use-after-scope` in the `--count` decrement.

`std::jthread` would cover this, but libc++ on macOS does not provide it, so add a
`join_guard` next to the other test guards and join explicitly. It is declared after
the objects the threads capture, so it is destroyed first and joins before they go
away.

Joining right after the spawn loop instead would be simpler, but this test exists to
exercise threading issues under TSAN, which relies on the io_context being pumped by
the `ASSERT_TIMELY` below while the workers are still calling `run`. The guard keeps
that overlap and only changes the failure path.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 5 <noreply@anthropic.com>

## Patch
### nano/rpc_test/rpc.cpp
```diff
@@ -1939,23 +1939,23 @@ TEST (rpc, version)
 	auto const rpc_ctx = add_rpc (system, node1);
 	boost::property_tree::ptree request1;
 	request1.put ("action", "version");
-	test_response response1 (request1, rpc_ctx.rpc->listening_port (), *system.io_ctx);
-	ASSERT_TIMELY (5s, response1.status != 0);
-	ASSERT_EQ (200, response1.status);
-	ASSERT_EQ ("1", response1.json.get<std::string> ("rpc_version"));
+	auto response1 = test_response::send (request1, rpc_ctx.rpc->listening_port (), *system.io_ctx);
+	ASSERT_TIMELY (5s, response1->status != 0);
+	ASSERT_EQ (200, response1->status);
+	ASSERT_EQ ("1", response1->json.get<std::string> ("rpc_version"));
 	{
 		auto transaction (node1->store.tx_begin_read ());
-		ASSERT_EQ (std::to_string (node1->store.meta.get_version (transaction)), response1.json.get<std::string> ("store_version"));
+		ASSERT_EQ (std::to_string (node1->store.meta.get_version (transaction)), response1->json.get<std::string> ("store_version"));
 	}
-	ASSERT_EQ (std::to_string (node1->network_params.network.protocol_version), response1.json.get<std::string> ("protocol_version"));
-	ASSERT_EQ (boost::str (boost::format ("Nano %1%") % NANO_VERSION_STRING), response1.json.get<std::string> ("node_vendor"));
-	ASSERT_EQ (node1->store.get_vendor (), response1.json.get<std::string> ("store_vendor"));
+	ASSERT_EQ (std::to_string (node1->network_params.network.protocol_version), response1->json.get<std::string> ("protocol_version"));
+	ASSERT_EQ (boost::str (boost::format ("Nano %1%") % NANO_VERSION_STRING), response1->json.get<std::string> ("node_vendor"));
+	ASSERT_EQ (node1->store.get_vendor (), response1->json.get<std::string> ("store_vendor"));
 	auto network_label (node1->network_params.network.get_current_network_as_string ());
-	ASSERT_EQ (network_label, response1.json.get<std::string> ("network"));
+	ASSERT_EQ (network_label, response1->json.get<std::string> ("network"));
 	auto genesis_open (node1->latest (nano::dev::genesis_key.pub));
-	ASSERT_EQ (genesis_open.to_string (), response1.json.get<std::string> ("network_identifier"));
-	ASSERT_EQ (BUILD_INFO, response1.json.get<std::string> ("build_info"));
-	auto headers (response1.resp.base ());
+	ASSERT_EQ (genesis_open.to_string (), response1->json.get<std::string> ("network_identifier"));
+	ASSERT_EQ (BUILD_INFO, response1->json.get<std::string> ("build_info"));
+	auto headers (response1->resp.base ());
 	auto allow (headers.at ("Allow"));
 	auto content_type (headers.at ("Content-Type"));
 	auto access_control_allow_origin (headers.at ("Access-Control-Allow-Origin"));
@@ -6857,24 +6857,24 @@ TEST (rpc, simultaneous_calls)
 	request.put ("account", nano::dev::genesis_key.pub.to_account ());
 
 	constexpr auto num = 100;
-	std::array<std::unique_ptr<test_response>, num> test_responses;
+	std::array<std::shared_ptr<test_response>, num> test_responses;
 	for (int i = 0; i < num; ++i)
 	{
-		test_responses[i] = std::make_unique<test_response> (request, *system.io_ctx);
+		test_responses[i] = test_response::prepare (request, *system.io_ctx);
 	}
 
 	std::promise<void> promise;
 	std::atomic<int> count{ num };
+	nano::test::join_guard threads;
 	for (int i = 0; i < num; ++i)
 	{
-		std::thread ([&test_responses, &promise, &count, i, port = rpc->listening_port ()] () {
+		threads.spawn ([&test_responses, &promise, &count, i, port = rpc->listening_port ()] () {
 			test_responses[i]->run (port);
 			if (--count == 0)
 			{
 				promise.set_value ();
 			}
-		})
-		.detach ();
+		});
 	}
 
 	auto future = promise.get_future ();
```

### nano/rpc_test/rpc_context.cpp
```diff
@@ -21,10 +21,10 @@ nano::test::rpc_context::rpc_context (std::shared_ptr<nano::rpc> & rpc_a, std::s
 
 void nano::test::wait_response_impl (nano::test::system & system, rpc_context const & rpc_ctx, boost::property_tree::ptree & request, std::chrono::duration<double, std::nano> const & time, boost::property_tree::ptree & response_json)
 {
-	test_response response (request, rpc_ctx.rpc->listening_port (), *system.io_ctx);
-	ASSERT_TIMELY (time, response.status != 0);
-	ASSERT_EQ (200, response.status);
-	response_json = response.json;
+	auto response = test_response::send (request, rpc_ctx.rpc->listening_port (), *system.io_ctx);
+	ASSERT_TIMELY (time, response->status != 0);
+	ASSERT_EQ (200, response->status);
+	response_json = response->json;
 }
 
 boost::property_tree::ptree nano::test::wait_response (nano::test::system & system, rpc_context const & rpc_ctx, boost::property_tree::ptree & request, std::chrono::duration<double, std::nano> const & time)
@@ -37,11 +37,11 @@ boost::property_tree::ptree nano::test::wait_response (nano::test::system & syst
 void nano::test::wait_responses_impl (nano::test::system & system, rpc_context const & rpc_ctx, std::vector<boost::property_tree::ptree> & requests, std::chrono::duration<double, std::nano> const & time, std::vector<boost::property_tree::ptree> & responses)
 {
 	// Start every request before waiting so they are in flight simultaneously
-	std::vector<std::unique_ptr<test_response>> in_flight;
+	std::vector<std::shared_ptr<test_response>> in_flight;
 	in_flight.reserve (requests.size ());
 	for (auto & request : requests)
 	{
-		in_flight.push_back (std::make_unique<test_response> (request, rpc_ctx.rpc->listening_port (), *system.io_ctx));
+		in_flight.push_back (test_response::send (request, rpc_ctx.rpc->listening_port (), *system.io_ctx));
 	}
 	ASSERT_TIMELY (time, std::all_of (in_flight.begin (), in_flight.end (), [] (auto const & response) { return response->status != 0; }));
 	for (auto const & response : in_flight)
```

### nano/rpc_test/test_response.cpp
```diff
@@ -8,22 +8,27 @@
 
 #include <boost/property_tree/json_parser.hpp>
 
-nano::test::test_response::test_response (boost::property_tree::ptree const & request_a, boost::asio::io_context & io_ctx_a) :
-	request (request_a),
-	sock (io_ctx_a)
+std::shared_ptr<nano::test::test_response> nano::test::test_response::prepare (boost::property_tree::ptree const & request, boost::asio::io_context & io_ctx)
 {
+	return std::make_shared<test_response> (private_tag{}, request, io_ctx);
 }
 
-nano::test::test_response::test_response (boost::property_tree::ptree const & request_a, uint16_t port_a, boost::asio::io_context & io_ctx_a) :
-	request (request_a),
-	sock (io_ctx_a)
+std::shared_ptr<nano::test::test_response> nano::test::test_response::send (boost::property_tree::ptree const & request, uint16_t port, boost::asio::io_context & io_ctx)
 {
-	run (port_a);
+	auto result = prepare (request, io_ctx);
+	result->run (port);
+	return result;
 }
 
-void nano::test::test_response::run (uint16_t port_a)
+nano::test::test_response::test_response (private_tag, boost::property_tree::ptree const & request, boost::asio::io_context & io_ctx) :
+	request{ request },
+	sock{ io_ctx }
 {
-	sock.async_connect (nano::tcp_endpoint (boost::asio::ip::address_v6::loopback (), port_a), [this] (boost::system::error_code const & ec) {
+}
+
+void nano::test::test_response::run (uint16_t port)
+{
+	sock.async_connect (nano::tcp_endpoint (boost::asio::ip::address_v6::loopback (), port), [this, /* lifetime guard */ this_s = shared_from_this ()] (boost::system::error_code const & ec) {
 		if (!ec)
 		{
 			std::stringstream ostream;
@@ -34,10 +39,10 @@ void nano::test::test_response::run (uint16_t port_a)
 			ostream.flush ();
 			req.body () = ostream.str ();
 			req.prepare_payload ();
-			boost::beast::http::async_write (sock, req, [this] (boost::system::error_code const & ec, size_t bytes_transferred) {
+			boost::beast::http::async_write (sock, req, [this, /* lifetime guard */ this_s = shared_from_this ()] (boost::system::error_code const & ec, size_t bytes_transferred) {
 				if (!ec)
 				{
-					boost::beast::http::async_read (sock, sb, resp, [this] (boost::system::error_code const & ec, size_t bytes_transferred) {
+					boost::beast::http::async_read (sock, sb, resp, [this, /* lifetime guard */ this_s = shared_from_this ()] (boost::system::error_code const & ec, size_t bytes_transferred) {
 						if (!ec)
 						{
 							std::stringstream body (resp.body ());
@@ -68,4 +73,4 @@ void nano::test::test_response::run (uint16_t port_a)
 			status = 400;
 		}
 	});
-}
\ No newline at end of file
+}
```

### nano/rpc_test/test_response.hpp
```diff
@@ -1,19 +1,43 @@
 #pragma once
 
+#include <boost/asio/io_context.hpp>
 #include <boost/asio/ip/tcp.hpp>
 #include <boost/beast/core/flat_buffer.hpp>
 #include <boost/beast/http.hpp>
 #include <boost/property_tree/ptree.hpp>
 
+#include <atomic>
+#include <memory>
+
 namespace nano::test
 {
-class test_response
+/**
+ * Performs a single HTTP request against an RPC server and captures the response.
+ *
+ * The in-flight async operations hold a reference to this object, so it stays alive until the
+ * request either completes or the io_context is destroyed. Callers are free to drop their handle
+ * at any point, which is what happens whenever a test gives up on a request after its deadline
+ * expires.
+ */
+class test_response : public std::enable_shared_from_this<test_response>
 {
+	// Only used to keep the constructor effectively private while remaining usable by `make_shared`
+	struct private_tag
+	{
+	};
+
+public:
+	// Creates a response object without sending the request, use `run` to send it
+	static std::shared_ptr<test_response> prepare (boost::property_tree::ptree const & request, boost::asio::io_context &);
+	// Creates a response object and sends the request immediately
+	static std::shared_ptr<test_response> send (boost::property_tree::ptree const & request, uint16_t port, boost::asio::io_context &);
+
+	test_response (private_tag, boost::property_tree::ptree const & request, boost::asio::io_context &);
+
+	void run (uint16_t port);
+
 public:
-	test_response (boost::property_tree::ptree const & request_a, boost::asio::io_context & io_ctx_a);
-	test_response (boost::property_tree::ptree const & request_a, uint16_t port_a, boost::asio::io_context & io_ctx_a);
-	void run (uint16_t port_a);
-	boost::property_tree::ptree const & request;
+	boost::property_tree::ptree const request;
 	boost::asio::ip::tcp::socket sock;
 	boost::property_tree::ptree json;
 	boost::beast::flat_buffer sb;
```

### nano/test_common/testutil.hpp
```diff
@@ -15,8 +15,10 @@
 #include <atomic>
 #include <chrono>
 #include <condition_variable>
+#include <deque>
 #include <mutex>
 #include <string>
+#include <thread>
 
 #define GTEST_TEST_ERROR_CODE(expression, text, actual, expected, fail)                       \
 	GTEST_AMBIGUOUS_ELSE_BLOCKER_                                                             \
@@ -143,6 +145,38 @@ class start_stop_guard
 	std::tuple<Ts &...> refs;
 };
 
+/**
+ * Owns a set of worker threads and joins them all on destruction
+ * Declare it after everything the threads reference, so they are joined before those objects go out of scope
+ */
+class join_guard
+{
+public:
+	join_guard () = default;
+	join_guard (join_guard const &) = delete;
+	join_guard & operator= (join_guard const &) = delete;
+
+	~join_guard ()
+	{
+		for (auto & thread : threads)
+		{
+			if (thread.joinable ())
+			{
+				thread.join ();
+			}
+		}
+	}
+
+	template <class T>
+	void spawn (T && func)
+	{
+		threads.emplace_back (std::forward<T> (func));
+	}
+
+private:
+	std::deque<std::thread> threads;
+};
+
 template <class... Ts>
 class stop_guard
 {
```
