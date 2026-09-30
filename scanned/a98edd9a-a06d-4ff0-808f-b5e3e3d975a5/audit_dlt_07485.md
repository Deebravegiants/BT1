# [?] Fix race condition between starting HTTP server thread and setting EventBase()

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2015-08-28
Source: https://github.com/dogecoin/dogecoin/commit/3a174cd400c6c239539d4c0c10b557c3e0615212
Type: security-commit

## Details
Fix race condition between starting HTTP server thread and setting EventBase()

Split StartHTTPServer into InitHTTPServer and StartHTTPServer to give
clients a window to register their handlers without race conditions.

Thanks @ajweiss for figuring this out.

## Patch
### src/httpserver.cpp
```diff
@@ -320,7 +320,7 @@ static void HTTPWorkQueueRun(WorkQueue<HTTPClosure>* queue)
     queue->Run();
 }
 
-bool StartHTTPServer(boost::thread_group& threadGroup)
+bool InitHTTPServer()
 {
     struct evhttp* http = 0;
     struct event_base* base = 0;
@@ -366,19 +366,25 @@ bool StartHTTPServer(boost::thread_group& threadGroup)
         return false;
     }
 
-    LogPrint("http", "Starting HTTP server\n");
+    LogPrint("http", "Initialized HTTP server\n");
     int workQueueDepth = std::max((long)GetArg("-rpcworkqueue", DEFAULT_HTTP_WORKQUEUE), 1L);
-    int rpcThreads = std::max((long)GetArg("-rpcthreads", DEFAULT_HTTP_THREADS), 1L);
-    LogPrintf("HTTP: creating work queue of depth %d and %d worker threads\n", workQueueDepth, rpcThreads);
+    LogPrintf("HTTP: creating work queue of depth %d\n", workQueueDepth);
+
     workQueue = new WorkQueue<HTTPClosure>(workQueueDepth);
+    eventBase = base;
+    eventHTTP = http;
+    return true;
+}
 
-    threadGroup.create_thread(boost::bind(&ThreadHTTP, base, http));
+bool StartHTTPServer(boost::thread_group& threadGroup)
+{
+    LogPrint("http", "Starting HTTP server\n");
+    int rpcThreads = std::max((long)GetArg("-rpcthreads", DEFAULT_HTTP_THREADS), 1L);
+    LogPrintf("HTTP: starting %d worker threads\n", rpcThreads);
+    threadGroup.create_thread(boost::bind(&ThreadHTTP, eventBase, eventHTTP));
 
     for (int i = 0; i < rpcThreads; i++)
         threadGroup.create_thread(boost::bind(&HTTPWorkQueueRun, workQueue));
-
-    eventBase = base;
-    eventHTTP = http;
     return true;
 }
 
```

### src/httpserver.h
```diff
@@ -20,7 +20,14 @@ struct event_base;
 class CService;
 class HTTPRequest;
 
-/** Start HTTP server */
+/** Initialize HTTP server.
+ * Call this before RegisterHTTPHandler or EventBase().
+ */
+bool InitHTTPServer();
+/** Start HTTP server.
+ * This is separate from InitHTTPServer to give users race-condition-free time
+ * to register their handlers between InitHTTPServer and StartHTTPServer.
+ */
 bool StartHTTPServer(boost::thread_group& threadGroup);
 /** Interrupt HTTP server threads */
 void InterruptHTTPServer();
```

### src/init.cpp
```diff
@@ -618,14 +618,16 @@ bool AppInitServers(boost::thread_group& threadGroup)
 {
     RPCServer::OnStopped(&OnRPCStopped);
     RPCServer::OnPreCommand(&OnRPCPreCommand);
-    if (!StartHTTPServer(threadGroup))
+    if (!InitHTTPServer())
         return false;
     if (!StartRPC())
         return false;
     if (!StartHTTPRPC())
         return false;
     if (GetBoolArg("-rest", false) && !StartREST())
         return false;
+    if (!StartHTTPServer(threadGroup))
+        return false;
     return true;
 }
 
```
