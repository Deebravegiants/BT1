# [?] core/bloombits: fix deadlock when matcher session hits an error (#347)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2023-09-26
Source: https://github.com/ava-labs/avalanchego/commit/95d320f81de8ad9a95912bdfa927dfbd1ce90916
Type: security-commit

## Details
core/bloombits: fix deadlock when matcher session hits an error (#347)

When MatcherSession encounters an error, it attempts to close the session.
Closing waits for all goroutines to finish, including the 'distributor'.
However, the distributor will not exit until all requests have returned.

This patch fixes the issue by delivering the (empty) result to the distributor
before calling Close().

## Patch
### core/bloombits/matcher.go
```diff
@@ -640,13 +640,16 @@ func (s *MatcherSession) Multiplex(batch int, wait time.Duration, mux chan chan
 			request <- &Retrieval{Bit: bit, Sections: sections, Context: s.ctx}
 
 			result := <-request
+
+			// Deliver a result before s.Close() to avoid a deadlock
+			s.deliverSections(result.Bit, result.Sections, result.Bitsets)
+
 			if result.Error != nil {
 				s.errLock.Lock()
 				s.err = result.Error
 				s.errLock.Unlock()
 				s.Close()
 			}
-			s.deliverSections(result.Bit, result.Sections, result.Bitsets)
 		}
 	}
 }
```
