# [?] fix: splitstore: remove deadlock around waiting for sync

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-05-11
Source: https://github.com/filecoin-project/lotus/commit/f4a3207ede353f55e51204ac4ebfa2279a785003
Type: security-commit

## Details
fix: splitstore: remove deadlock around waiting for sync

## Patch
### blockstore/splitstore/splitstore_compact.go
```diff
@@ -1114,13 +1114,17 @@ func (s *SplitStore) walkChain(ts *types.TipSet, inclState, inclMsgs abi.ChainEp
 					if err := walkBlock(c); err != nil {
 						return xerrors.Errorf("error walking block (cid: %s): %w", c, err)
 					}
+
+					if err := s.checkYield(); err != nil {
+						return xerrors.Errorf("check yield: %w", err)
+					}
 				}
 				return nil
 			})
 		}
 
 		if err := g.Wait(); err != nil {
-			return err
+			return xerrors.Errorf("walkBlock workers errored: %w", err)
 		}
 	}
 
@@ -1153,8 +1157,8 @@ func (s *SplitStore) walkObject(c cid.Cid, visitor ObjectVisitor, f func(cid.Cid
 	}
 
 	// check this before recursing
-	if err := s.checkYield(); err != nil {
-		return 0, err
+	if err := s.checkClosing(); err != nil {
+		return 0, xerrors.Errorf("check closing: %w", err)
 	}
 
 	var links []cid.Cid
@@ -1222,8 +1226,8 @@ func (s *SplitStore) walkObjectIncomplete(c cid.Cid, visitor ObjectVisitor, f, m
 	}
 
 	// check this before recursing
-	if err := s.checkYield(); err != nil {
-		return sz, err
+	if err := s.checkClosing(); err != nil {
+		return sz, xerrors.Errorf("check closing: %w", err)
 	}
 
 	var links []cid.Cid
```
