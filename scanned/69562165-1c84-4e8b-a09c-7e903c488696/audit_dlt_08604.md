# [?] fix(indexer): fix potential panic in chain reconciliation logic during backfill (#12813)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2025-01-08
Source: https://github.com/filecoin-project/lotus/commit/31c3a6072198952e4f3f136ae06c1b0f13ccbc84
Type: security-commit

## Details
fix(indexer): fix potential panic in chain reconciliation logic during backfill (#12813)

Co-authored-by: Peter Rabbitson <ribasushi@leporine.io>

## Patch
### chain/index/reconcile.go
```diff
@@ -236,10 +236,10 @@ func (si *SqliteIndexer) backfillIndex(ctx context.Context, tx *sql.Tx, head *ty
 			log.Infof("reached stop height %d; backfilled %d tipsets", stopAfter, totalApplied)
 			return nil
 		}
-
+		height := currTs.Height()
 		currTs, err = si.cs.GetTipSetFromKey(ctx, currTs.Parents())
 		if err != nil {
-			return xerrors.Errorf("failed to walk chain at height %d: %w", currTs.Height(), err)
+			return xerrors.Errorf("failed to walk chain beyond height %d: %w", height, err)
 		}
 	}
 
```
