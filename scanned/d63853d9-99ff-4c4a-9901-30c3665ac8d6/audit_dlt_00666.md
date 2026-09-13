# [?] Merge bitcoin/bitcoin#35614: HTTPServer: Prevent race condition between worker thread and I/O thread

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-07-03
Source: https://github.com/bitcoin/bitcoin/commit/239d6c526080927bcdf7cec13fcdde27359cfb30
Type: security-commit

## Details
Merge bitcoin/bitcoin#35614: HTTPServer: Prevent race condition between worker thread and I/O thread

f595daf1dd01e9730e0eafbc46b2e22eeb9f33fe test: ensure HTTPServer race condition is fixed (Matthew Zipkin)
b98b10c07236cd37d96f14e4a220af11dc8a0fc6 test: introduce a worker thread in http socket error test (Matthew Zipkin)
922b08d375351e313dd92fbefdb166ee27838ac0 test: socket error handling in HTTPServer using ErrorSock mock socket (Matthew Zipkin)
73da2a8a52f75b20cf3adfe36ad3804c41047d81 http: prevent race condition between worker thread and I/O thread (Matthew Zipkin)

Pull request description:

  This prevents a losing race condition that could prevent the server from reading any more requests from an HTTP client.

  Found and reported by the fuzzing department: https://github.com/dergoegge/bitcoin/commit/7fe5f54497c86f216b619e340939447504e87dcb

  The Race:

  A connected socket can either be written to or read from based on the result of `GenerateWaitSockets()`. That method checks the `HTTPRemoteClient` flag `m_send_ready`. If it's `true` the implication is that there is data in the client's send buffer ready to go. Once that data is sent and the buffer is empty, `MaybeSendBytesFromBuffer()` sets it `false` again.

  The sad case was when a worker thread calling `WriteReply()` adds data to the send buffer, but before it sets `m_send_ready` to `true`, the I/O thread sends that data and empties the buffer. With the buffer unexpectedly empty, `WriteReply()` sets `m_send_ready` to `true`.

  The effect of this is that the socket will stay in "write" mode with nothing to write. With nothing to write, `MaybeSendBytesFromBuffer()` never sets it back to `false` and the socket is stuck forever.

  The Fix:

  Simply move `m_send_ready = true` inside the block of `WriteReply()` where `m_send_mutex` is still held. This prevents the I/O thread from emptying the send buffer while the worker thread is setting the flag.

  Testing:

  To observe the race condition, revert the first commit `"http: prevent race condition between worker thread and I/O thread"` and run the unit test from the  remainder of the branch. I like to see the logs:

  `test_bitcoin --log_level=all  --run_test=httpserver_tests -- --printtoconsole --debug=http --debug=lock'

  The test will fail with a small probability. The socket will get stuck and the test will abort after a 60 second timeout. To garuntee the race condition loses and fail the test every time, slow down `WriteReply()` in the worker thread:

  ```diff
  diff --git a/src/httpserver.cpp b/src/httpserver.cpp
  index 99e30ff663..b0c7b516d8 100644
  --- a/src/httpserver.cpp
  +++ b/src/httpserver.cpp
  @@ -614,6 +614,7 @@ void HTTPRequest::WriteReply(HTTPStatusCode status, std::span<const std::byte> r
       } else {
           // Inform HTTPServer I/O that data is ready to be sent to this client
           // in the next loop iteration.
  +        std::this_thread::sleep_for(500ms);
           m_client->m_send_ready = true;
       }

  ```

  With the first commit (the fix) back in place, slowing down the worker thread like this won't fail the test.

  Bonus:

  The unit test is spread over three commits. First, a method of the socket testing setup is templated so a mock socket that intentionally raises an error can be inserted. The unit test added in that commit covers a race condition that was fixed in #35182 in response to https://github.com/bitcoin/bitcoin/pull/35182/changes#r3358889539 so we get the added benefit of covering an error path, and guaranteeing coverage of both "optimistic send" (directly from worker thread) and regular send (from a tick in the I/O loop thread).

  The next commit adds a worker thread to the unit test, at which point a race condition is possible but very unlikely because all requests are sent at once. Finally, we spread out the requests in the top commit and make the race condition much easier to catch.

ACKs for top commit:
  janb84:
    crACK f595daf1dd01e9730e0eafbc46b2e22eeb9f33fe
  dergoegge:
    utACK f595daf1dd01e9730e0eafbc46b2e22eeb9f33fe
  theStack:
    Code-review ACK f595daf1dd01e9730e0eafbc46b2e22eeb9f33fe

Tree-SHA512: 451982fd72724c4115e371fc6392605693d6c3207f00ffebcf027aae9253f7974b5b1165b9f46c91b5436d7fe60c7d27316fb0b79f729ab0bf8f32db2530075f

### src/httpserver.cpp
```diff
@@ -595,6 +595,16 @@ void HTTPRequest::WriteReply(HTTPStatusCode status, std::span<const std::byte> r
         // data. The original data will go out of scope when WriteReply() returns.
         // This is analogous to the memcpy() in libevent's evbuffer_add()
         m_client->m_send_buffer.insert(m_client->m_send_buffer.end(), reply_body.begin(), reply_body.end());
+
+        // If the buffer already held data, the I/O thread is (or soon will be)
+        // draining it, so flag that there is more data to send. This must happen
+        // while holding m_send_mutex and while the buffer is known non-empty:
+        // setting m_send_ready after releasing the lock would race with the I/O
+        // thread draining the buffer to empty and clearing m_send_ready in
+        // between, leaving m_send_ready set on an empty buffer. The I/O loop would
+        // then only ever poll the socket for writeability, never read the client's
+        // next request, and wedge the connection.
+        if (!send_buffer_was_empty) m_client->m_send_ready = true;
     }
 
     LogDebug(
@@ -611,10 +621,6 @@ void HTTPRequest::WriteReply(HTTPStatusCode status, std::span<const std::byte> r
     // of waiting for the next iteration of the I/O loop.
     if (send_buffer_was_empty) {
         m_client->MaybeSendBytesFromBuffer();
-    } else {
-        // Inform HTTPServer I/O that data is ready to be sent to this client
-        // in the next loop iteration.
-        m_client->m_send_ready = true;
     }
 
     // Signal to the I/O loop that we are ready to handle the next request.
@@ -935,7 +941,12 @@ HTTPServer::IOReadiness HTTPServer::GenerateWaitSockets() const
 
         // Check if client is ready to send data. Don't try to receive again
         // until the send buffer is cleared (all data sent to client).
-        Sock::Event event = (http_client->m_send_ready ? Sock::SendEvent : Sock::RecvEvent);
+        // Keep this as a separate critical section from the m_sock_mutex one above:
+        // never hold m_sock_mutex and m_send_mutex at the same time here.
+        // MaybeSendBytesFromBuffer() locks m_send_mutex then m_sock_mutex, so nesting
+        // them in the opposite order here would risk a lock-order inversion deadlock.
+        const bool send_ready{WITH_LOCK(http_client->m_send_mutex, return http_client->m_send_ready;)};
+        Sock::Event event = (send_ready ? Sock::SendEvent : Sock::RecvEvent);
         io_readiness.events_per_sock.emplace(sock, Sock::Events{event});
         io_readiness.httpclients_per_sock.emplace(sock, http_client);
     }
```

### src/httpserver.h
```diff
@@ -483,11 +483,14 @@ class HTTPRemoteClient
     /// @}
 
     /**
-     * Set true by worker threads after writing a response to m_send_buffer.
-     * Set false by the HTTPServer I/O thread after flushing m_send_buffer.
-     * Checked in the HTTPServer I/O loop to avoid locking m_send_mutex if there's nothing to send.
-     */
-    std::atomic_bool m_send_ready{false};
+    * Set true by worker threads after writing a response to m_send_buffer.
+    * Set false by the HTTPServer I/O thread after flushing m_send_buffer.
+    * Checked in the HTTPServer I/O loop to decide whether to poll the socket for
+    * writeability or readability.
+    * Guarded by m_send_mutex so it stays consistent with m_send_buffer's emptiness:
+    * the two must always be updated together under the same lock.
+    */
+    bool m_send_ready GUARDED_BY(m_send_mutex){false};
 
     /**
      * Mutex that serializes the Send() and Recv() calls on `m_sock`. Reading
```

### src/test/httpserver_tests.cpp
```diff
@@ -5,8 +5,10 @@
 #include <httpserver.h>
 #include <rpc/protocol.h>
 #include <test/util/common.h>
+#include <test/util/logging.h>
 #include <test/util/setup_common.h>
 #include <util/string.h>
+#include <util/threadpool.h>
 
 #include <boost/test/unit_test.hpp>
 
@@ -628,4 +630,160 @@ BOOST_AUTO_TEST_CASE(http_server_socket_tests)
     server.StopListening();
 }
 
+BOOST_AUTO_TEST_CASE(http_socket_error_tests)
+{
+    // Create a tiny threadpool for the HTTPRequest handler
+    ThreadPool workers("http");
+    workers.Start(1);
+
+    // Hard-code the server's request handler to respond to each request with
+    // an incremented block count. Handle the replies in the worker thread.
+    std::atomic<int> height{0};
+    HTTPServer server{[&](std::shared_ptr<HTTPRequest> req) {
+        auto item = [req, &height]() {
+            const int h = height.fetch_add(1);
+            req->WriteReply(HTTP_OK, strprintf("height: %d\n", h));
+        };
+        // Can't call BOOST_REQUIRE from worker thread
+        Assert(workers.Submit(std::move(item)));
+    }};
+
+    // All replies will be the same size
+    static constexpr std::size_t reply_length = std::string_view{
+        "HTTP/1.1 200 OK\r\n"
+        "Date: Thu, 01 Jan 2026 00:00:00 GMT\r\n"           // All RFC1123 dates are 29 characters
+        "Content-Length: 10\r\n"
+        "Content-Type: text/html; charset=ISO-8859-1\r\n"
+        "\r\n"
+        "height: 0\n"
+    }.size();
+
+    /**
+     * A mocked Sock derived from DynSock whose Send() only succeeds when there is more than
+     * one reply being sent (send buffer length > reply_length). Otherwise it returns
+     * a recoverable error (WSAEAGAIN).
+     *
+     * After it sends successfully once, it continues to always succeed.
+     *
+     * Useful for testing "try again" logic around non-blocking socket Send() failures.
+     */
+    class ErrorSock : public DynSock
+    {
+    public:
+        explicit ErrorSock(std::shared_ptr<Pipes> pipes) : DynSock{std::move(pipes)} {}
+        DynSock& operator=(Sock&&) override { assert(false); return *this; }
+
+        ssize_t Send(const void* buf, size_t len, int flags) const override
+        {
+            if (len <= reply_length && !m_have_sent) {
+                #ifdef WIN32
+                WSASetLastError(WSAEWOULDBLOCK);
+                #else
+                errno = WSAEAGAIN;
+                #endif
+                return -1;
+            } else {
+                m_have_sent = true;
+                return DynSock::Send(buf, len, flags);
+            }
+        }
+
+        mutable bool m_have_sent{false};
+    };
+
+    // Simpler server startup than the last test
+    CService addr_bind{Lookup("0.0.0.0", /*portDefault=*/0, /*fAllowLookup=*/false).value()};
+    BOOST_REQUIRE(server.BindAndStartListening(addr_bind));
+    server.StartSocketsThreads();
+
+    // Prepare initial requests
+    int num_requests = 2;
+    // Use keep-alive so the server holds the connection open for all requests.
+    std::string keepalive_request{full_request};
+    keepalive_request.replace(keepalive_request.find("Connection: close"), 17, "Connection: keep-alive");
+    // Combine all requests so they are read from the socket on a single iteration of the I/O loop
+    std::string all_requests;
+    for (int i = 0; i < num_requests; i++) {
+        all_requests += keepalive_request;
+    }
+
+    // Watch the log messages to ensure that the first two replies were sent
+    // together. This indicates the non-optimistic send path was used
+    // because a reply was already sitting in the send buffer when a second reply
+    // was added.
+    DebugLogHelper find_two_replies{strprintf("Sent %d bytes to client", reply_length * 2),
+                                    [&](const std::string* s) {
+                                        return true;
+                                    }};
+    // Last reply should be sent on its own by optimistic send path, because
+    // the send buffer was empty when the reply was written.
+    DebugLogHelper find_one_reply{strprintf("Sent %d bytes to client", reply_length),
+                                  [&](const std::string* s) {
+                                      return true;
+                                   }};
+
+    // Connect the ErrorSock as mock client with the preloaded data and get a handle on the I/O pipes
+    std::shared_ptr<ErrorSock::Pipes> mock_client_socket_pipes{
+        ConnectClient<ErrorSock>(std::as_bytes(std::span(all_requests)))
+    };
+
+    // Wait up to one minute for the last reply from the server
+    std::string actual;
+    char buf[0x10000] = {};
+    int attempts = 6000;
+    while (attempts > 0)
+    {
+        ssize_t bytes_read = mock_client_socket_pipes->send.GetBytes(buf, sizeof(buf), 0);
+        if (bytes_read > 0) {
+            actual.append(buf, bytes_read);
+            if (actual.find(strprintf("height: %d", num_requests - 1)) != std::string::npos) {
+                break;
+            }
+        }
+        std::this_thread::sleep_for(10ms);
+        --attempts;
+    }
+
+    // Send the third request.
+    // If there was a race between WriteReply() in the worker thread setting m_send_ready=true
+    // and SocketHandlerConnected() in the I/O thread flushing the send buffer,
+    // then the socket would be stuck in write mode with nothing to write,
+    // the server would never read from the socket, and this request would time out.
+    // Wait a second to ensure both the worker thread and I/O thread are idle.
+    // If we send the next request too soon it might get accepted by the server before
+    // it gets wedged shut.
+    std::this_thread::sleep_for(1000ms);
+    mock_client_socket_pipes->recv.PushBytes(keepalive_request.data(), keepalive_request.size());
+    num_requests++;
+
+    // Wait up to one minute for reply
+    attempts = 6000;
+    while (attempts > 0)
+    {
+        ssize_t bytes_read = mock_client_socket_pipes->send.GetBytes(buf, sizeof(buf), 0);
+        if (bytes_read > 0) {
+            actual.append(buf, bytes_read);
+            if (actual.find(strprintf("height: %d", num_requests - 1)) != std::string::npos) {
+                break;
+            }
+        }
+        std::this_thread::sleep_for(10ms);
+        --attempts;
+    }
+
+    // All replies were received
+    for (int i = 0; i < num_requests; i++) {
+        BOOST_REQUIRE(actual.find(strprintf("height: %d", i)) != std::string::npos);
+    }
+
+    // Close the keep-alive connection
+    server.DisconnectAllClients();
+
+    workers.Stop();
+
+    server.InterruptNet();
+    server.JoinSocketsThreads();
+    server.StopListening();
+}
+
 BOOST_AUTO_TEST_SUITE_END()
```

### src/test/util/setup_common.cpp
```diff
@@ -657,24 +657,6 @@ SocketTestingSetup::~SocketTestingSetup()
     CreateSock = m_create_sock_orig;
 }
 
-std::shared_ptr<DynSock::Pipes> SocketTestingSetup::ConnectClient(std::span<const std::byte> data)
-{
-    // I/O pipes for a mock Connected Socket we can read and write to.
-    auto connected_socket_pipes(std::make_shared<DynSock::Pipes>());
-
-    // Insert the payload
-    connected_socket_pipes->recv.PushBytes(data.data(), data.size());
-
-    // Create the Mock Connected Socket that represents a client.
-    // It needs I/O pipes but its queue can remain empty
-    std::unique_ptr<DynSock> connected_socket{std::make_unique<DynSock>(connected_socket_pipes)};
-
-    // Push into the queue of Accepted Sockets returned by the local CreateSock()
-    m_accepted_sockets.Push(std::move(connected_socket));
-
-    return connected_socket_pipes;
-}
-
 /**
  * @returns a real block (0000000000013b8ab2cd513b0261a14096412195a72a0c4827d229dcc7e0f7af)
  *      with 9 txs.
```

### src/test/util/setup_common.h
```diff
@@ -257,10 +257,18 @@ class SocketTestingSetup : public BasicTestingSetup
     ~SocketTestingSetup();
 
     /**
-     * Connect to the socket with a mock client (a DynSock) and send pre-loaded data.
+     * Connect to the socket with a mock client and send pre-loaded data.
      * Returns the I/O pipes from the mock client so we can read response data sent to it.
+     * Template parameter selects the socket type: DynSock by default.
      */
-    std::shared_ptr<DynSock::Pipes> ConnectClient(std::span<const std::byte> data);
+    template <typename T = DynSock>
+    std::shared_ptr<typename T::Pipes> ConnectClient(std::span<const std::byte> data)
+    {
+        auto connected_socket_pipes(std::make_shared<typename T::Pipes>());
+        connected_socket_pipes->recv.PushBytes(data.data(), data.size());
+        m_accepted_sockets.Push(std::make_unique<T>(connected_socket_pipes));
+        return connected_socket_pipes;
+    }
 
 private:
     //! Save the original value of CreateSock here and restore it when the test ends.
```
