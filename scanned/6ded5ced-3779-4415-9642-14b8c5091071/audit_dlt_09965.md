# [?] Prevent data race for `pathHandlers`

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2022-09-02
Source: https://github.com/ElementsProject/elements/commit/5def1b2a98c09e51eec3d6d0e7e5c8a82acfb501
Type: security-commit

## Details
Prevent data race for `pathHandlers`

Github-Pull: bitcoin/bitcoin#25983
Rebased-From: 4296dde28757d88a7076847484669fb202b47bc8

## Patch
### src/httpserver.cpp
```diff
@@ -143,7 +143,8 @@ static std::vector<CSubNet> rpc_allow_subnets;
 //! Work queue for handling longer requests off the event loop thread
 static std::unique_ptr<WorkQueue<HTTPClosure>> g_work_queue{nullptr};
 //! Handlers for (sub)paths
-static std::vector<HTTPPathHandler> pathHandlers;
+static Mutex g_httppathhandlers_mutex;
+static std::vector<HTTPPathHandler> pathHandlers GUARDED_BY(g_httppathhandlers_mutex);
 //! Bound listening sockets
 static std::vector<evhttp_bound_socket *> boundSockets;
 
@@ -244,6 +245,7 @@ static void http_request_cb(struct evhttp_request* req, void* arg)
     // Find registered handler for prefix
     std::string strURI = hreq->GetURI();
     std::string path;
+    LOCK(g_httppathhandlers_mutex);
     std::vector<HTTPPathHandler>::const_iterator i = pathHandlers.begin();
     std::vector<HTTPPathHandler>::const_iterator iend = pathHandlers.end();
     for (; i != iend; ++i) {
@@ -642,11 +644,13 @@ HTTPRequest::RequestMethod HTTPRequest::GetRequestMethod() const
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
