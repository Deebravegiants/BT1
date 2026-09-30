# [?] fix deadlock on miner module when failed to commit trie (#835)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2022-04-02
Source: https://github.com/bnb-chain/bsc/commit/05925da696fdfbcfa97a42e3f14b18361d237938
Type: security-commit

## Details
fix deadlock on miner module when failed to commit trie (#835)

## Patch
### core/state/statedb.go
```diff
@@ -1366,10 +1366,8 @@ func (s *StateDB) Commit(failPostCommitFunc func(), postCommitFuncs ...func() er
 					// Write any contract code associated with the state object
 					tasks <- func() {
 						// Write any storage changes in the state object to its storage trie
-						if err := obj.CommitTrie(s.db); err != nil {
-							taskResults <- err
-						}
-						taskResults <- nil
+						err := obj.CommitTrie(s.db)
+						taskResults <- err
 					}
 					tasksNum++
 				}
```
