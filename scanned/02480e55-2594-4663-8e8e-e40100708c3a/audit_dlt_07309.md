# [?] fix: remove pointless panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-04-18
Source: https://github.com/filecoin-project/lotus/commit/141c020b4e6adff675f4628be7d138a84f364c7b
Type: security-commit

## Details
fix: remove pointless panic

Technically, the block validator caught this panic. But it's pointless
because we have a _real_ mechanism to return the validation reason,
which we should have been using.

In general, panicing like this is a very bad idea because it's
non-obvious and, in this case, completely undocumented.

## Patch
### chain/consensus/iface.go
```diff
@@ -65,23 +65,16 @@ func ValidateBlockPubsub(ctx context.Context, cns Consensus, self bool, msg *pub
 
 	stats.Record(ctx, metrics.BlockReceived.M(1))
 
-	recordFailureFlagPeer := func(what string) {
-		// bv.Validate will flag the peer in that case
-		panic(what)
-	}
-
 	blk, what, err := decodeAndCheckBlock(msg)
 	if err != nil {
 		log.Error("got invalid block over pubsub: ", err)
-		recordFailureFlagPeer(what)
 		return pubsub.ValidationReject, what
 	}
 
 	// validate the block meta: the Message CID in the header must match the included messages
 	err = validateMsgMeta(ctx, blk)
 	if err != nil {
 		log.Warnf("error validating message metadata: %s", err)
-		recordFailureFlagPeer("invalid_block_meta")
 		return pubsub.ValidationReject, "invalid_block_meta"
 	}
 
@@ -91,7 +84,6 @@ func ValidateBlockPubsub(ctx context.Context, cns Consensus, self bool, msg *pub
 			log.Warn("ignoring block msg: ", err)
 			return pubsub.ValidationIgnore, reject
 		}
-		recordFailureFlagPeer(reject)
 		return pubsub.ValidationReject, reject
 	}
 
```
