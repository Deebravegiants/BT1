# [?] Fix potential vulnerabilities in ConsensusLeader code

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-12-04
Source: https://github.com/Zilliqa/zq1/commit/9636644b38df6bd2e064598481c8a83997230e66
Type: security-commit

## Details
Fix potential vulnerabilities in ConsensusLeader code

## Patch
### src/libConsensus/ConsensusLeader.cpp
```diff
@@ -265,6 +265,8 @@ bool ConsensusLeader::ProcessMessageCommitCore(
     [[gnu::unused]] State nextstate) {
   LOG_MARKER();
 
+  lock_guard<mutex> g(m_mutex);
+
   // Initial checks
   // ==============
 
@@ -298,49 +300,47 @@ bool ConsensusLeader::ProcessMessageCommitCore(
   }
 
   bool result = false;
-  {
-    // Update internal state
-    // =====================
-    lock_guard<mutex> g(m_mutex);
 
-    if (!CheckState(action)) {
-      return false;
-    }
+  // Update internal state
+  // =====================
 
-    // 33-byte commit
-    m_commitPoints.emplace_back(commitPoint);
-    m_commitPointMap.at(backupID) = commitPoint;
-    m_commitMap.at(backupID) = true;
+  if (!CheckState(action)) {
+    return false;
+  }
 
-    m_commitCounter++;
+  // 33-byte commit
+  m_commitPoints.emplace_back(commitPoint);
+  m_commitPointMap.at(backupID) = commitPoint;
+  m_commitMap.at(backupID) = true;
 
-    if (m_commitCounter % 10 == 0) {
-      LOG_GENERAL(INFO, "Received " << m_commitCounter << " out of "
-                                    << m_numForConsensus << ".");
-    }
+  m_commitCounter++;
 
-    // Redundant commits
-    if (m_commitCounter > m_numForConsensus) {
-      m_commitRedundantPointMap.at(backupID) = commitPoint;
-      m_commitRedundantMap.at(backupID) = true;
-      m_commitRedundantCounter++;
-    }
+  if (m_commitCounter % 10 == 0) {
+    LOG_GENERAL(INFO, "Received " << m_commitCounter << " out of "
+                                  << m_numForConsensus << ".");
+  }
 
-    if (NUM_CONSENSUS_SUBSETS > 1) {
-      // notify the waiting thread to start with subset creations and subset
-      // consensus.
-      if (m_commitCounter == m_committee.size()) {
-        lock_guard<mutex> g(m_mutexAnnounceSubsetConsensus);
-        m_allCommitsReceived = true;
-        cv_scheduleSubsetConsensus.notify_all();
-      }
-    } else {
-      if (m_commitCounter == m_numForConsensus) {
-        LOG_GENERAL(INFO, "Sufficient commits obtained. Required/Actual = "
-                              << m_commitCounter);
-        GenerateConsensusSubsets();
-        StartConsensusSubsets();
-      }
+  // Redundant commits
+  if (m_commitCounter > m_numForConsensus) {
+    m_commitRedundantPointMap.at(backupID) = commitPoint;
+    m_commitRedundantMap.at(backupID) = true;
+    m_commitRedundantCounter++;
+  }
+
+  if (NUM_CONSENSUS_SUBSETS > 1) {
+    // notify the waiting thread to start with subset creations and subset
+    // consensus.
+    if (m_commitCounter == m_committee.size()) {
+      lock_guard<mutex> g(m_mutexAnnounceSubsetConsensus);
+      m_allCommitsReceived = true;
+      cv_scheduleSubsetConsensus.notify_all();
+    }
+  } else {
+    if (m_commitCounter == m_numForConsensus) {
+      LOG_GENERAL(INFO, "Sufficient commits obtained. Required/Actual = "
+                            << m_commitCounter);
+      GenerateConsensusSubsets();
+      StartConsensusSubsets();
     }
   }
 
@@ -480,7 +480,7 @@ bool ConsensusLeader::ProcessMessageResponseCore(
   }
 
   // Check the subset id
-  if (subsetID >= NUM_CONSENSUS_SUBSETS) {
+  if (subsetID >= m_consensusSubsets.size()) {
     LOG_GENERAL(WARNING, "Error: Subset ID (" << subsetID
                                               << ") >= NUM_CONSENSUS_SUBSETS: "
                                               << NUM_CONSENSUS_SUBSETS);
@@ -861,6 +861,7 @@ bool ConsensusLeader::StartConsensus(
         LOG_GENERAL(
             INFO, "Sufficient commits obtained after timeout. Required = "
                       << m_numForConsensus << " Actual = " << m_commitCounter);
+        lock_guard<mutex> g(m_mutex);
         GenerateConsensusSubsets();
         StartConsensusSubsets();
       }
```
