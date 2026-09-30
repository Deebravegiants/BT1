# [?] core/bloombits: avoid crash when storing errors of different type (#23437)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-08-24
Source: https://github.com/ethereum/go-ethereum/commit/8e0771c21825e9621f29d6c4018038b4505a59f4
Type: security-commit

## Details
core/bloombits: avoid crash when storing errors of different type (#23437)

This fixes a rare crash which could occur when two different errors happened
in the same bloombits.MatcherSession.

## Patch
### core/bloombits/matcher.go
```diff
@@ -510,8 +510,9 @@ type MatcherSession struct {
 	closer sync.Once     // Sync object to ensure we only ever close once
 	quit   chan struct{} // Quit channel to request pipeline termination
 
-	ctx context.Context // Context used by the light client to abort filtering
-	err atomic.Value    // Global error to track retrieval failures deep in the chain
+	ctx     context.Context // Context used by the light client to abort filtering
+	err     error           // Global error to track retrieval failures deep in the chain
+	errLock sync.Mutex
 
 	pend sync.WaitGroup
 }
@@ -529,10 +530,10 @@ func (s *MatcherSession) Close() {
 
 // Error returns any failure encountered during the matching session.
 func (s *MatcherSession) Error() error {
-	if err := s.err.Load(); err != nil {
-		return err.(error)
-	}
-	return nil
+	s.errLock.Lock()
+	defer s.errLock.Unlock()
+
+	return s.err
 }
 
 // allocateRetrieval assigns a bloom bit index to a client process that can either
@@ -630,7 +631,9 @@ func (s *MatcherSession) Multiplex(batch int, wait time.Duration, mux chan chan
 
 			result := <-request
 			if result.Error != nil {
-				s.err.Store(result.Error)
+				s.errLock.Lock()
+				s.err = result.Error
+				s.errLock.Unlock()
 				s.Close()
 			}
 			s.deliverSections(result.Bit, result.Sections, result.Bitsets)
```
