# [?] core/state: avoid data race (#29924)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-06-04
Source: https://github.com/ethereum/go-ethereum/commit/125fb1ff5855134b040e295f380eeecff29af375
Type: security-commit

## Details
core/state: avoid data race (#29924)

## Patch
### core/state/statedb.go
```diff
@@ -1211,8 +1211,8 @@ func (s *StateDB) commit(deleteEmptyObjects bool) (*stateUpdate, error) {
 			}
 			lock.Lock()
 			updates[obj.addrHash] = update
-			lock.Unlock()
 			s.StorageCommits = time.Since(start) // overwrite with the longest storage commit runtime
+			lock.Unlock()
 			return nil
 		})
 	}
```
