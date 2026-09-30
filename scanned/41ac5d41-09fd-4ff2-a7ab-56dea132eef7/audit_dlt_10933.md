# [?] Fix potential race condition

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-12-21
Source: https://github.com/Zilliqa/zq1/commit/776306bf4a62012394020dc89b112cde4c26d7e1
Type: security-commit

## Details
Fix potential race condition

## Patch
### src/libNode/MicroBlockPostProcessing.cpp
```diff
@@ -138,7 +138,7 @@ bool Node::ProcessMicroblockConsensus(const vector<unsigned char>& message,
 void Node::CommitMicroBlockConsensusBuffer() {
   lock_guard<mutex> g(m_mutexMicroBlockConsensusBuffer);
 
-  for (const auto& i : m_microBlockConsensusBuffer[m_mediator.m_consensusID]) {
+  for (const auto i : m_microBlockConsensusBuffer[m_mediator.m_consensusID]) {
     auto runconsensus = [this, i]() {
       ProcessMicroblockConsensusCore(i.second, MessageOffset::BODY, i.first);
     };
```
