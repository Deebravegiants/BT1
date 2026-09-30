# [?] Fix m_syncType may have data race issue

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-02-25
Source: https://github.com/Zilliqa/zq1/commit/8657152bf9d0080ee8907f9e914ae5f28adcfc3e
Type: security-commit

## Details
Fix m_syncType may have data race issue

## Patch
### src/libLookup/Lookup.cpp
```diff
@@ -62,6 +62,7 @@ Lookup::Lookup(Mediator& mediator) : m_mediator(mediator) {
   if (LOOKUP_NODE_MODE) {
     SetDSCommitteInfo();
   }
+  m_syncType.store(SyncType::NO_SYNC);
 }
 
 Lookup::~Lookup() {}
@@ -3572,7 +3573,7 @@ bool Lookup::ProcessVCGetLatestDSTxBlockFromSeed(const bytes& message,
 }
 
 void Lookup::SetSyncType(SyncType syncType) {
-  m_syncType = syncType;
+  m_syncType.store(syncType);
   LOG_EPOCH(INFO, m_mediator.m_currentEpochNum,
             "Set sync type to " << syncType);
 }
```

### src/libLookup/Lookup.h
```diff
@@ -84,7 +84,7 @@ class Lookup : public Executable {
   std::condition_variable cv_startPoWSubmission;
 
   /// To indicate which type of synchronization is using
-  SyncType m_syncType = SyncType::NO_SYNC;
+  std::atomic<SyncType> m_syncType;  // = SyncType::NO_SYNC;
 
   void SetAboveLayer();
 
@@ -335,7 +335,7 @@ class Lookup : public Executable {
 
   bool Execute(const bytes& message, unsigned int offset, const Peer& from);
 
-  inline SyncType GetSyncType() const { return m_syncType; }
+  inline SyncType GetSyncType() const { return m_syncType.load(); }
   void SetSyncType(SyncType syncType);
 
   bool m_fetchedOfflineLookups = false;
```
