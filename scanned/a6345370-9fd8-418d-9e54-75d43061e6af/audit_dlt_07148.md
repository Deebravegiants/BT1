# [?] http-server: guard against crashes from unhandled exceptions

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-01-28
Source: https://github.com/bitcoin/bitcoin/commit/45930a79412dc45f9d391cd7689d029fa4f0189e
Type: security-commit

## Details
http-server: guard against crashes from unhandled exceptions

Currently, if an exception is thrown at the top-level HTTP request
handler (prior to invoking the command), the program crashes.

Ideally, each handler should catch all exceptions internally and
be responsible for sanitizing them and crafting the client response.
This is because only the handler knows the correct response format,
which differs per server type. However, because this cannot always
be guaranteed, it is safer to also catch exceptions in the top-level
server code, log the unexpected error, and disconnect the socket.

This both guards against crashes caused by uncaught exceptions and
prevents the client from hanging indefinitely while waiting for a
response that will never arrive.

The following diff can be used to trigger the crash in master
(just run single node functional tests like feature_shutdown.py):
```
diff --git a/src/httprpc.cpp b/src/httprpc.cpp
--- a/src/httprpc.cpp
+++ b/src/httprpc.cpp
@@ -103,6 +103,9 @@

 static bool HTTPReq_JSONRPC(const std::any& context, HTTPRequest* req)
 {
+    static int i = 0; // skip initial requests as they are used in the RPC warmup phase.
+    if (i++ > 3) throw std::runtime_error("error from json rpc handler");
+
     // JSONRPC handles only POST
     if (req->GetRequestMethod() != HTTPRequest::POST) {
         req->WriteReply(HTTP_BAD_METHOD, "JSONRPC server handles only POST requests");

```

Note:
This leaves a TODO in the code because error responses should eventually
be specialized per server type. REST clients expect plain text responses,
while JSON-RPC clients expect a JSON error object.
The TODO is there because this is not consistently enforced everywhere
in the current codebase, and we should tackle them all at once.

## Patch
### src/httpserver.cpp
```diff
@@ -327,7 +327,24 @@ static void http_request_cb(struct evhttp_request* req, void* arg)
 
     // Dispatch to worker thread
     if (i != iend) {
-        std::unique_ptr<HTTPWorkItem> item(new HTTPWorkItem(std::move(hreq), path, i->handler));
+        auto item = std::make_unique<HTTPWorkItem>(std::move(hreq), path, [fn = i->handler](HTTPRequest* req, const std::string& path_inner) {
+            std::string err_msg;
+            try {
+                return fn(req, path_inner);
+            } catch (const std::exception& e) {
+                LogWarning("Unexpected error while processing request for '%s'. Error msg: '%s'", req->GetURI(), e.what());
+                err_msg = e.what();
+            } catch (...) {
+                LogWarning("Unknown error while processing request for '%s'", req->GetURI());
+                err_msg = "unknown error";
+            }
+            // Reply so the client doesn't hang waiting for the response.
+            req->WriteHeader("Connection", "close");
+            // TODO: Implement specific error formatting for the REST and JSON-RPC servers responses.
+            req->WriteReply(HTTP_INTERNAL_SERVER_ERROR, err_msg);
+            return false;
+        });
+
         assert(g_work_queue);
         if (g_work_queue->Enqueue(item.get())) {
             (void)item.release(); /* if true, queue took ownership */
```
