# [?] Fix race condition where GetWorkServer will put difficulty soln for ds_difficulty mining

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2020-08-27
Source: https://github.com/Zilliqa/zq1/commit/e8ab74077a5c05e81c203faad97daf36db824084
Type: security-commit

## Details
Fix race condition where GetWorkServer will put difficulty soln for ds_difficulty mining

## Patch
### src/libServer/GetWorkServer.cpp
```diff
@@ -66,6 +66,9 @@ bool GetWorkServer::StartServer() {
 
 // StartMining starts mining
 bool GetWorkServer::StartMining(const PoWWorkPackage& wp) {
+  // Keep track of current difficulty for this round of mining
+  m_currentTargetDifficulty = wp.difficulty;
+
   // clear the last result
   {
     lock_guard<mutex> g(m_mutexResult);
@@ -90,6 +93,7 @@ bool GetWorkServer::StartMining(const PoWWorkPackage& wp) {
 // StopMining stops mining and clear result
 void GetWorkServer::StopMining() {
   m_isMining = false;
+  m_currentTargetDifficulty = 0;
 
   lock_guard<mutex> g(m_mutexResult);
   m_curResult.success = false;
@@ -173,8 +177,8 @@ ethash_mining_result_t GetWorkServer::VerifySubmit(const string& nonce,
 }
 
 // UpdateCurrentResult check and update new result
-bool GetWorkServer::UpdateCurrentResult(
-    const ethash_mining_result_t& newResult) {
+bool GetWorkServer::UpdateCurrentResult(const ethash_mining_result_t& newResult,
+                                        const uint8_t difficulty) {
   if (!newResult.success) {
     LOG_GENERAL(WARNING, "newResult is not success");
     return false;
@@ -186,12 +190,13 @@ bool GetWorkServer::UpdateCurrentResult(
 
   if (!m_curResult.success) {
     // accept the new result directly if current result is false
-    accept = true;
+    accept = (difficulty == m_currentTargetDifficulty);
   } else {
     // accept the new result if it less or equal than current one
     auto new_hash = POW::StringToBlockhash(newResult.result);
     auto cur_hash = POW::StringToBlockhash(m_curResult.result);
-    accept = ethash::is_less_or_equal(new_hash, cur_hash);
+    accept = ethash::is_less_or_equal(new_hash, cur_hash) &&
+             (difficulty == m_currentTargetDifficulty);
   }
 
   if (accept) {
@@ -238,6 +243,8 @@ bool GetWorkServer::submitWork(const string& _nonce, const string& _header,
     return false;
   }
 
+  const uint8_t difficulty = m_currentTargetDifficulty;
+
   string nonce = _nonce;
   string header = _header;
   string mixdigest = _mixdigest;
@@ -259,7 +266,7 @@ bool GetWorkServer::submitWork(const string& _nonce, const string& _header,
 
   auto result = VerifySubmit(nonce, header, mixdigest, boundary);
 
-  return UpdateCurrentResult(result);
+  return UpdateCurrentResult(result, difficulty);
   ;
 }
 
```

### src/libServer/GetWorkServer.h
```diff
@@ -121,6 +121,9 @@ class GetWorkServer : public AbstractStubServer {
   std::mutex m_mutexResult;
   std::condition_variable m_cvGotResult;
 
+  // an indicator for current mining target difficulty
+  std::atomic<uint8_t> m_currentTargetDifficulty{};
+
  public:
   // Returns the singleton instance.
   static GetWorkServer &GetInstance();
@@ -146,7 +149,8 @@ class GetWorkServer : public AbstractStubServer {
   // Protocol for GetResult
   ethash_mining_result_t GetResult(int waitTime);
 
-  bool UpdateCurrentResult(const ethash_mining_result_t &newResult);
+  bool UpdateCurrentResult(const ethash_mining_result_t &newResult,
+                           const uint8_t difficulty);
 
   // RPC methods
   virtual Json::Value getWork();
```
