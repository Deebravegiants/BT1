# [?] http: Avoid crash when g_thread_http was never started

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-05-18
Source: https://github.com/litecoin-project/litecoin/commit/faf45d1f1f997c316fc4c611a23c4456533eefe9
Type: security-commit

## Details
http: Avoid crash when g_thread_http was never started

g_thread_http can not be joined when it is not joinable. Avoid crashing
the node by adding the required check and add a test.

## Patch
### src/httpserver.cpp
```diff
@@ -421,15 +421,15 @@ bool UpdateHTTPServerLogging(bool enable) {
 #endif
 }
 
-static std::thread threadHTTP;
+static std::thread g_thread_http;
 static std::vector<std::thread> g_thread_http_workers;
 
 void StartHTTPServer()
 {
     LogPrint(BCLog::HTTP, "Starting HTTP server\n");
     int rpcThreads = std::max((long)gArgs.GetArg("-rpcthreads", DEFAULT_HTTP_THREADS), 1L);
     LogPrintf("HTTP: starting %d worker threads\n", rpcThreads);
-    threadHTTP = std::thread(ThreadHTTP, eventBase);
+    g_thread_http = std::thread(ThreadHTTP, eventBase);
 
     for (int i = 0; i < rpcThreads; i++) {
         g_thread_http_workers.emplace_back(HTTPWorkQueueRun, workQueue, i);
@@ -467,7 +467,7 @@ void StopHTTPServer()
     boundSockets.clear();
     if (eventBase) {
         LogPrint(BCLog::HTTP, "Waiting for HTTP event thread to exit\n");
-        threadHTTP.join();
+        if (g_thread_http.joinable()) g_thread_http.join();
     }
     if (eventHTTP) {
         evhttp_free(eventHTTP);
```

### test/functional/rpc_users.py
```diff
@@ -99,5 +99,13 @@ def run_test(self):
 
         self.test_auth(self.nodes[1], self.rpcuser, self.rpcpassword)
 
+        self.log.info('Check that failure to write cookie file will abort the node gracefully')
+        self.stop_node(0)
+        cookie_file = os.path.join(get_datadir_path(self.options.tmpdir, 0), self.chain, '.cookie.tmp')
+        os.mkdir(cookie_file)
+        init_error = 'Error: Unable to start HTTP server. See debug log for details.'
+        self.nodes[0].assert_start_raises_init_error(expected_msg=init_error)
+
+
 if __name__ == '__main__':
     HTTPBasicsTest().main()
```
