# [?] Merge #14993: rpc: Fix data race (UB) in InterruptRPC()

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2018-12-19
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/cf4fb07ca99d72b48055537e673e96e8352e8520
Type: security-commit

## Details
Merge #14993: rpc: Fix data race (UB) in InterruptRPC()

Summary:
Backport [[https://github.com/bitcoin/bitcoin/pull/14993/files | PR14993]] . Fixes T733 .

6c10037f72073eecc674c313580ef50a4f1e1e44 rpc: Fix data race (UB) in InterruptRPC() (practicalswift)

Pull request description:

  Fix data race (UB) in `InterruptRPC()`.

  Before:

  ```
  $ ./configure --with-sanitizers=thread
  $ make
  $ test/functional/test_runner.py feature_shutdown.py
  …
  SUMMARY: ThreadSanitizer: data race rpc/server.cpp:314 in InterruptRPC()
  …
  ALL                 | ✖ Failed  | 2 s (accumulated)
  ```

  After:

  ```
  $ ./configure --with-sanitizers=thread
  $ make
  $ test/functional/test_runner.py feature_shutdown.py
  …
  ALL                 | ✓ Passed  | 3 s (accumulated)
  ```

Test Plan: `ninja check-all` ; run tests with TSAN

Reviewers: Fabien, #bitcoin_abc

Reviewed By: Fabien, #bitcoin_abc

Maniphest Tasks: T733

Differential Revision: https://reviews.bitcoinabc.org/D5177

## Patch
### src/rpc/server.cpp
```diff
@@ -26,7 +26,7 @@
 #include <set>
 #include <unordered_map>
 
-static bool fRPCRunning = false;
+static std::atomic<bool> g_rpc_running{false};
 static bool fRPCInWarmup = true;
 static std::string rpcWarmupStatus("RPC server started");
 static CCriticalSection cs_rpcWarmup;
@@ -423,14 +423,14 @@ bool CRPCTable::appendCommand(const std::string &name,
 
 void StartRPC() {
     LogPrint(BCLog::RPC, "Starting RPC\n");
-    fRPCRunning = true;
+    g_rpc_running = true;
     g_rpcSignals.Started();
 }
 
 void InterruptRPC() {
     LogPrint(BCLog::RPC, "Interrupting RPC\n");
     // Interrupt e.g. running longpolls
-    fRPCRunning = false;
+    g_rpc_running = false;
 }
 
 void StopRPC() {
@@ -441,7 +441,7 @@ void StopRPC() {
 }
 
 bool IsRPCRunning() {
-    return fRPCRunning;
+    return g_rpc_running;
 }
 
 void SetRPCWarmupStatus(const std::string &newStatus) {
```
