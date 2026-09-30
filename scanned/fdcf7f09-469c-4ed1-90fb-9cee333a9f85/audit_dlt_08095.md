# [?] graph/db: fix potential nil pointer derefs

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-07-28
Source: https://github.com/lightningnetwork/lnd/commit/858c064ca29898c89cf17940170374d3143155e6
Type: security-commit

## Details
graph/db: fix potential nil pointer derefs

Here, we fix two bugs that could lead to a nil pointer dereference.
Both are caused by refering to policies that may be nil at the
call-site.

## Patch
### graph/db/sql_store.go
```diff
@@ -1188,7 +1188,7 @@ func (s *SQLStore) ForEachNodeCached(ctx context.Context,
 				var cachedInPolicy *models.CachedEdgePolicy
 				if inPolicy != nil {
 					cachedInPolicy = models.NewCachedPolicy(
-						p2,
+						inPolicy,
 					)
 					cachedInPolicy.ToNodePubKey =
 						toNodeCallback
@@ -1197,19 +1197,21 @@ func (s *SQLStore) ForEachNodeCached(ctx context.Context,
 				}
 
 				var inboundFee lnwire.Fee
-				outPolicy.InboundFee.WhenSome(
-					func(fee lnwire.Fee) {
-						inboundFee = fee
-					},
-				)
+				if outPolicy != nil {
+					outPolicy.InboundFee.WhenSome(
+						func(fee lnwire.Fee) {
+							inboundFee = fee
+						},
+					)
+				}
 
 				directedChannel := &DirectedChannel{
 					ChannelID: e.ChannelID,
 					IsNode1: nodePub ==
 						e.NodeKey1Bytes,
 					OtherNode:    e.NodeKey2Bytes,
 					Capacity:     e.Capacity,
-					OutPolicySet: p1 != nil,
+					OutPolicySet: outPolicy != nil,
 					InPolicy:     cachedInPolicy,
 					InboundFee:   inboundFee,
 				}
```
