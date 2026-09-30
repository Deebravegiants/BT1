# [?] Merge #19006: rpc: Avoid crash when g_thread_http was never started

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-05-20
Source: https://github.com/litecoin-project/litecoin/commit/bd5ec7c5284d839d403a0b859b4e6ef0ee50bcbc
Type: security-commit

## Details
Merge #19006: rpc: Avoid crash when g_thread_http was never started

faf45d1f1f997c316fc4c611a23c4456533eefe9 http: Avoid crash when g_thread_http was never started (MarcoFalke)
fa12a37b27f0570a551b8c103ea6537ee4a8e399 test: Replace inline-comments with logs, pep8 formatting (MarcoFalke)
fa83b39ff3ae3fbad93df002915c0e5f99c104a9 init: Remove confusing and redundant InitError (MarcoFalke)

Pull request description:

  Avoid a crash during shutdown when the init sequence failed for some reason

ACKs for top commit:
  promag:
    Tested ACK faf45d1f1f997c316fc4c611a23c4456533eefe9.
  ryanofsky:
    Code review ACK faf45d1f1f997c316fc4c611a23c4456533eefe9. Thanks for updates, this is much easier to parse for me now. Since previous reviews: split out and reverted some cleanups & replaced chmod with mkdir in test
  hebasto:
    ACK faf45d1f1f997c316fc4c611a23c4456533eefe9, tested on Linux Mint 19.3 with the following patch:

Tree-SHA512: 59632bf01c999e65c724e2728ac103250ccd8b0b16fac19d3a2a82639ab73e4f2efb86c78e63c588a5954625d8d0cf9545e2a7e070e6e15d2a54beeb50e00b61

## Patch
### src/httprpc.cpp
```diff
@@ -9,7 +9,6 @@
 #include <httpserver.h>
 #include <rpc/protocol.h>
 #include <rpc/server.h>
-#include <ui_interface.h>
 #include <util/strencodings.h>
 #include <util/system.h>
 #include <util/translation.h>
@@ -251,9 +250,6 @@ static bool InitRPCAuthentication()
     {
         LogPrintf("Using random cookie authentication.\n");
         if (!GenerateAuthCookie(&strRPCUserColonPass)) {
-            uiInterface.ThreadSafeMessageBox(
-                _("Error: A fatal internal error occurred, see debug.log for details"), // Same message as AbortNode
-                "", CClientUIInterface::MSG_ERROR);
             return false;
         }
     } else {
```

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
@@ -20,6 +20,7 @@
 import configparser
 import sys
 
+
 def call_with_auth(node, user, password):
     url = urllib.parse.urlparse(node.url)
     headers = {"Authorization": "Basic " + str_to_b64str('{}:{}'.format(user, password))}
@@ -64,9 +65,9 @@ def setup_chain(self):
         self.password = lines[3]
 
         with open(os.path.join(get_datadir_path(self.options.tmpdir, 0), "bitcoin.conf"), 'a', encoding='utf8') as f:
-            f.write(rpcauth+"\n")
-            f.write(rpcauth2+"\n")
-            f.write(rpcauth3+"\n")
+            f.write(rpcauth + "\n")
+            f.write(rpcauth2 + "\n")
+            f.write(rpcauth3 + "\n")
         with open(os.path.join(get_datadir_path(self.options.tmpdir, 1), "bitcoin.conf"), 'a', encoding='utf8') as f:
             f.write("rpcuser={}\n".format(self.rpcuser))
             f.write("rpcpassword={}\n".format(self.rpcpassword))
@@ -76,32 +77,35 @@ def test_auth(self, node, user, password):
         assert_equal(200, call_with_auth(node, user, password).status)
 
         self.log.info('Wrong...')
-        assert_equal(401, call_with_auth(node, user, password+'wrong').status)
+        assert_equal(401, call_with_auth(node, user, password + 'wrong').status)
 
         self.log.info('Wrong...')
-        assert_equal(401, call_with_auth(node, user+'wrong', password).status)
+        assert_equal(401, call_with_auth(node, user + 'wrong', password).status)
 
         self.log.info('Wrong...')
-        assert_equal(401, call_with_auth(node, user+'wrong', password+'wrong').status)
+        assert_equal(401, call_with_auth(node, user + 'wrong', password + 'wrong').status)
 
     def run_test(self):
-
-        ##################################################
-        # Check correctness of the rpcauth config option #
-        ##################################################
+        self.log.info('Check correctness of the rpcauth config option')
         url = urllib.parse.urlparse(self.nodes[0].url)
 
         self.test_auth(self.nodes[0], url.username, url.password)
         self.test_auth(self.nodes[0], 'rt', self.rtpassword)
         self.test_auth(self.nodes[0], 'rt2', self.rt2password)
         self.test_auth(self.nodes[0], self.user, self.password)
 
-        ###############################################################
-        # Check correctness of the rpcuser/rpcpassword config options #
-        ###############################################################
+        self.log.info('Check correctness of the rpcuser/rpcpassword config options')
         url = urllib.parse.urlparse(self.nodes[1].url)
 
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
-    HTTPBasicsTest ().main ()
+    HTTPBasicsTest().main()
```
