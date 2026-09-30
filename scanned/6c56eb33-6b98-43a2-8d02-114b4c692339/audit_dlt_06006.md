# [?] core/bloombits: fix deadlock when matcher session hits an error (#28184)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-09-25
Source: https://github.com/etclabscore/core-geth/commit/c2cfe35f121cb88650b4d90c958bcc4214d0ce7f
Type: security-commit

## Details
core/bloombits: fix deadlock when matcher session hits an error (#28184)

When MatcherSession encounters an error, it attempts to close the session.
Closing waits for all goroutines to finish, including the 'distributor'. However, the
distributor will not exit until all requests have returned.

This patch fixes the issue by delivering the (empty) result to the distributor
before calling Close().

## Patch
### core/bloombits/matcher.go
```diff
@@ -630,13 +630,16 @@ func (s *MatcherSession) Multiplex(batch int, wait time.Duration, mux chan chan
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
