# [?] Fix nondeterministic receive-order assertion in chunkconsumer receive-3 test

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-08-04
Source: https://github.com/onflow/flow-go/commit/c60b4a18370ee5d02a9b030262273dcc847454c4
Type: security-commit

## Details
Fix nondeterministic receive-order assertion in chunkconsumer receive-3 test

## Patch
### engine/verification/fetcher/chunkconsumer/consumer_test.go
```diff
@@ -56,8 +56,9 @@ func TestProduceConsume(t *testing.T) {
 			<-consumer.Done()
 
 			// expect the mock engine receive only the first 3 calls (since it is blocked on those, hence no
-			// new job is fetched to process).
-			require.Equal(t, locators[:3], called)
+			// new job is fetched to process). The 3 concurrent workers append in nondeterministic
+			// order, so assert the multiset rather than the exact sequence.
+			require.ElementsMatch(t, locators[:3], called)
 		})
 	})
 
```
