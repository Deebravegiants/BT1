# [?] avoid uint64 overflow for viewID check

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-11-08
Source: https://github.com/harmony-one/harmony/commit/2658355275a2ec3a9165f78ba4af09eab90c352f
Type: security-commit

## Details
avoid uint64 overflow for viewID check

## Patch
### consensus/checks.go
```diff
@@ -168,7 +168,7 @@ func (consensus *Consensus) onViewChangeSanityCheck(recvMsg *FBFTMessage) bool {
 			Msg("[onViewChangeSanityCheck] ViewChanging ID Is Low")
 		return false
 	}
-	if recvMsg.ViewID-consensus.GetViewChangingID() > MaxViewIDDiff {
+	if recvMsg.ViewID > consensus.GetViewChangingID() && recvMsg.ViewID-consensus.GetViewChangingID() > MaxViewIDDiff {
 		consensus.getLogger().Debug().
 			Msg("[onViewChangeSanityCheck] Received viewID that is MaxViewIDDiff (249) further from the current viewID!")
 		return false
```
