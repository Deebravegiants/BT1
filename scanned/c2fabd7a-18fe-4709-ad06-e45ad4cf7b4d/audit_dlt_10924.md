# [?] Merge pull request #1784 from Zilliqa/fix/crash

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-08-29
Source: https://github.com/Zilliqa/zq1/commit/5c464af994d24263d4e7fb61d0dc18f94e392c7f
Type: security-commit

## Details
Merge pull request #1784 from Zilliqa/fix/crash

Fix access null pointer

## Patch
### src/libNode/Node.cpp
```diff
@@ -281,8 +281,10 @@ void Node::Init() {
   // set consensusID for first epoch to 1.
   LOG_MARKER();
 
-  m_retriever->CleanAll();
-  m_retriever.reset();
+  if (m_retriever) {
+    m_retriever->CleanAll();
+    m_retriever.reset();
+  }
   m_mediator.m_dsBlockChain.Reset();
   m_mediator.m_txBlockChain.Reset();
   m_mediator.m_blocklinkchain.Reset();
```
