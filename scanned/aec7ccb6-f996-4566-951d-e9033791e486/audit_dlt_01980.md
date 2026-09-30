# [?] Fix the fix for race condition in Finder unit test (#2504)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2021-03-24
Source: https://github.com/hyperledger/fabric/commit/576d186581cc8acb39e21ffbc56d96de9f7ec9eb
Type: security-commit

## Details
Fix the fix for race condition in Finder unit test (#2504)

At the end of the unit test, correctly stop the goroutine used to ensure that commit messages are available to read at the point the listener attaches.

Signed-off-by: Mark S. Lewis <mark_lewis@uk.ibm.com>

## Patch
### internal/pkg/gateway/commit/finder_test.go
```diff
@@ -32,6 +32,7 @@ func TestFinder(t *testing.T) {
 				select {
 				case commitSend <- msg:
 				case <-done:
+					return
 				}
 			}
 		}()
```
