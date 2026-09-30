# [?] eth/downloader: fix rare crash when parent header missing in db (#27945)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-08-17
Source: https://github.com/etclabscore/core-geth/commit/649deb69f3b93c2ac35bdf910ec9d3a68fc2fb77
Type: security-commit

## Details
eth/downloader: fix rare crash when parent header missing in db (#27945)

ReadSkeletonHeader can return nil if the header is missing, so we should
not access fields on it. Note that calling .Hash() on a nil header is fine, so there 
is no need to actually check for nil.

Co-authored-by: Martin Holst Swende <martin@swende.se>

## Patch
### eth/downloader/skeleton.go
```diff
@@ -648,7 +648,7 @@ func (s *skeleton) processNewHead(head *types.Header, final *types.Header, force
 	}
 	if parent := rawdb.ReadSkeletonHeader(s.db, number-1); parent.Hash() != head.ParentHash {
 		if force {
-			log.Warn("Beacon chain forked", "ancestor", parent.Number, "hash", parent.Hash(), "want", head.ParentHash)
+			log.Warn("Beacon chain forked", "ancestor", number-1, "hash", parent.Hash(), "want", head.ParentHash)
 		}
 		return true
 	}
```
