# [?] Merge bitcoin/bitcoin#25983: Prevent data race for `pathHandlers`

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2022-09-07
Source: https://github.com/dashpay/dash/commit/ab1c90a325bbfbb0e74ea766a9a957a16539eb06
Type: security-commit

## Details
Merge bitcoin/bitcoin#25983: Prevent data race for `pathHandlers`

4296dde28757d88a7076847484669fb202b47bc8 Prevent data race for `pathHandlers` (Hennadii Stepanov)

Pull request description:

  Fixes bitcoin/bitcoin#19341.

ACKs for top commit:
  ryanofsky:
    Code review ACK 4296dde28757d88a7076847484669fb202b47bc8. This should protect the vector. It also seems to make the http_request_cb callback single threaded, but that seems ok, since it is just adding work queue items not actually processing requests.

Tree-SHA512: 1c3183100bbc80d8e83543da090b8f4521921cf30d444e3e4c87102bf7a1e67ccc4dfea7e9990ac49741b2a5708f259f4eced9d4049c20ae4e531461532a6aef

## Patch
### src/httpserver.cpp
```diff
@@ -157,7 +157,8 @@ static std::unique_ptr<WorkQueue<HTTPClosure>> g_work_queue{nullptr};
 //! List of 'external' RPC users (global variable, used by httprpc)
 std::vector<std::string> g_external_usernames;
 //! Handlers for (sub)paths
-static std::vector<HTTPPathHandler> pathHandlers;
+static Mutex g_httppathhandlers_mutex;
+static std::vector<HTTPPathHandler> pathHandlers GUARDED_BY(g_httppathhandlers_mutex);
 //! Bound listening sockets
 static std::vector<evhttp_bound_socket *> boundSockets;
 
@@ -250,6 +251,7 @@ static void http_request_cb(struct evhttp_request* req, void* arg)
     // Find registered handler for prefix
     std::string strURI = hreq->GetURI();
     std::string path;
+    LOCK(g_httppathhandlers_mutex);
     std::vector<HTTPPathHandler>::const_iterator i = pathHandlers.begin();
     std::vector<HTTPPathHandler>::const_iterator iend = pathHandlers.end();
     for (; i != iend; ++i) {
@@ -681,11 +683,13 @@ HTTPRequest::RequestMethod HTTPRequest::GetRequestMethod() const
 void RegisterHTTPHandler(const std::string &prefix, bool exactMatch, const HTTPRequestHandler &handler)
 {
     LogPrint(BCLog::HTTP, "Registering HTTP handler for %s (exactmatch %d)\n", prefix, exactMatch);
+    LOCK(g_httppathhandlers_mutex);
     pathHandlers.push_back(HTTPPathHandler(prefix, exactMatch, handler));
 }
 
 void UnregisterHTTPHandler(const std::string &prefix, bool exactMatch)
 {
+    LOCK(g_httppathhandlers_mutex);
     std::vector<HTTPPathHandler>::iterator i = pathHandlers.begin();
     std::vector<HTTPPathHandler>::iterator iend = pathHandlers.end();
     for (; i != iend; ++i)
```
