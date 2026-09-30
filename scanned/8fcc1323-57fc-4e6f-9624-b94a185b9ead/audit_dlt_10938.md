# [?] Fix crash of calling IsLookupNode

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-12-07
Source: https://github.com/Zilliqa/zq1/commit/83306e30b2a9c1cb4cfb538c37b5d92b42f94c7c
Type: security-commit

## Details
Fix crash of calling IsLookupNode

## Patch
### src/libLookup/Lookup.cpp
```diff
@@ -199,17 +199,19 @@ VectorOfLookupNode Lookup::GetLookupNodes() const {
 }
 
 bool Lookup::IsLookupNode(const PubKey& pubKey) const {
-  return std::find_if(GetLookupNodes().begin(), GetLookupNodes().end(),
+  VectorOfLookupNode lookups = GetLookupNodes();
+  return std::find_if(lookups.begin(), lookups.end(),
                       [&pubKey](const std::pair<PubKey, Peer>& node) {
                         return node.first == pubKey;
-                      }) != GetLookupNodes().end();
+                      }) != lookups.end();
 }
 
 bool Lookup::IsLookupNode(const Peer& peerInfo) const {
-  return std::find_if(GetLookupNodes().begin(), GetLookupNodes().end(),
+  VectorOfLookupNode lookups = GetLookupNodes();
+  return std::find_if(lookups.begin(), lookups.end(),
                       [&peerInfo](const std::pair<PubKey, Peer>& node) {
                         return node.second == peerInfo;
-                      }) != GetLookupNodes().end();
+                      }) != lookups.end();
 }
 
 void Lookup::SendMessageToLookupNodes(
```
