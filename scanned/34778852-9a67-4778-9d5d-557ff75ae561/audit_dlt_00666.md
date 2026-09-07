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
```

_Trimmed to 38 lines — full report: https://github.com/bitcoin/bitcoin/commit/239d6c526080927bcdf7cec13fcdde27359cfb30_
