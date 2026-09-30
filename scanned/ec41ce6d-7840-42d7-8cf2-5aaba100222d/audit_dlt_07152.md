# [?] Merge bitcoin/bitcoin#33007: test: fix `ReadTopologicalSet` unsigned integer overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-07-21
Source: https://github.com/bitcoin/bitcoin/commit/11c6a864c9ee3a9bbd65720517fd22c155fd9060
Type: security-commit

## Details
Merge bitcoin/bitcoin#33007: test: fix `ReadTopologicalSet` unsigned integer overflow

31c4e77a256c15c221dcc278883f6d3be55660b4 test: fix ReadTopologicalSet unsigned integer overflow (ismaelsadeeq)

Pull request description:

  This PR is a simple fix for a potential unsigned integer overflow in ReadTopologicalSet.
  We obtain the value of `mask` from fuzz input, which can be the maximum representable value.
  Adding 1 to it would then cause an overflow.

  The fix skips the addition when the read value is already the maximum.

  See https://github.com/bitcoin/bitcoin/pull/30605#discussion_r2215338569 for more context

ACKs for top commit:
  maflcko:
    lgtm ACK 31c4e77a256c15c221dcc278883f6d3be55660b4

Tree-SHA512: f58d7907f66a0de0ed8d4b1cad6a4971f65925a99f3c030537c21c4d84126b643257c65865242caf7d445b9cbb7a71a1816a9f870ab7520625c4c16cd41979cb

## Patch
### src/test/fuzz/cluster_linearize.cpp
```diff
@@ -304,7 +304,7 @@ SetType ReadTopologicalSet(const DepGraph<SetType>& depgraph, const SetType& tod
     try {
         reader >> VARINT(mask);
     } catch(const std::ios_base::failure&) {}
-    mask += non_empty;
+    if (mask != uint64_t(-1)) mask += non_empty;
 
     SetType ret;
     for (auto i : todo) {
```
