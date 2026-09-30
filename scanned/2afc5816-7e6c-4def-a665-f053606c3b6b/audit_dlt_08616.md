# [?] Merge pull request #10690 from filecoin-project/fix/remove-pointless-panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-04-21
Source: https://github.com/filecoin-project/lotus/commit/a503a0edaa66aa05e344749e0e6b1f43c80d172f
Type: security-commit

## Details
Merge pull request #10690 from filecoin-project/fix/remove-pointless-panic

fix: remove pointless panic

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
