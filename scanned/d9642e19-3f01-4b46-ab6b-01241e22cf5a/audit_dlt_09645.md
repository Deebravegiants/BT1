# [?] rpc: Fix data race (UB) in InterruptRPC()

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2018-12-18
Source: https://github.com/dogecoin/dogecoin/commit/bfdaf2d269adf108efd24023b37e3c77f0d0c8d9
Type: security-commit

## Details
rpc: Fix data race (UB) in InterruptRPC()

Cherry-picked from: 6c10037f7

## Patch
### src/rpc/server.cpp
```diff
@@ -29,7 +29,7 @@
 using namespace RPCServer;
 using namespace std;
 
-static bool fRPCRunning = false;
+static std::atomic<bool> g_rpc_running{false};
 static bool fRPCInWarmup = true;
 static std::string rpcWarmupStatus("RPC server started");
 static CCriticalSection cs_rpcWarmup;
@@ -325,7 +325,7 @@ bool CRPCTable::appendCommand(const std::string& name, const CRPCCommand* pcmd)
 bool StartRPC()
 {
     LogPrint("rpc", "Starting RPC\n");
-    fRPCRunning = true;
+    g_rpc_running = true;
     g_rpcSignals.Started();
     return true;
 }
@@ -334,7 +334,7 @@ void InterruptRPC()
 {
     LogPrint("rpc", "Interrupting RPC\n");
     // Interrupt e.g. running longpolls
-    fRPCRunning = false;
+    g_rpc_running = false;
 }
 
 void StopRPC()
@@ -347,7 +347,7 @@ void StopRPC()
 
 bool IsRPCRunning()
 {
-    return fRPCRunning;
+    return g_rpc_running;
 }
 
 void SetRPCWarmupStatus(const std::string& newStatus)
```
