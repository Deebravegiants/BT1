# [?] fix deadlock when failed to verify state root (#834)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2022-04-02
Source: https://github.com/bnb-chain/bsc/commit/f5a1c073bc9ac786652457719e5540f08abf87ec
Type: security-commit

## Details
fix deadlock when failed to verify state root (#834)

## Patch
### core/state/statedb.go
```diff
@@ -1415,14 +1415,15 @@ func (s *StateDB) Commit(failPostCommitFunc func(), postCommitFuncs ...func() er
 		if s.pipeCommit {
 			if commitErr == nil {
 				s.snaps.Snapshot(s.stateRoot).MarkValid()
+				close(verified)
 			} else {
 				// The blockchain will do the further rewind if write block not finish yet
+				close(verified)
 				if failPostCommitFunc != nil {
 					failPostCommitFunc()
 				}
 				log.Error("state verification failed", "err", commitErr)
 			}
-			close(verified)
 		}
 		return commitErr
 	}
```
