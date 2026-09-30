# [?] beacon/light: fix lock after lock deadlock (#34800)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-05-19
Source: https://github.com/ethereum/go-ethereum/commit/970e3cd6f01331fab4888d4f185f7081c88e029d
Type: security-commit

## Details
beacon/light: fix lock after lock deadlock (#34800)

## Patch
### beacon/light/committee_chain.go
```diff
@@ -182,6 +182,12 @@ func (s *CommitteeChain) Reset() {
 	s.chainmu.Lock()
 	defer s.chainmu.Unlock()
 
+	s.resetLocked()
+}
+
+// ResetLocked resets the committee chain without locking. The caller should hold
+// the chainmu lock.
+func (s *CommitteeChain) resetLocked() {
 	if err := s.rollback(0); err != nil {
 		log.Error("Error writing batch into chain database", "error", err)
 	}
@@ -201,22 +207,22 @@ func (s *CommitteeChain) CheckpointInit(bootstrap types.BootstrapData) error {
 	}
 	period := bootstrap.Header.SyncPeriod()
 	if err := s.deleteFixedCommitteeRootsFrom(period + 2); err != nil {
-		s.Reset()
+		s.resetLocked()
 		return err
 	}
 	if s.addFixedCommitteeRoot(period, bootstrap.CommitteeRoot) != nil {
-		s.Reset()
+		s.resetLocked()
 		if err := s.addFixedCommitteeRoot(period, bootstrap.CommitteeRoot); err != nil {
-			s.Reset()
+			s.resetLocked()
 			return err
 		}
 	}
 	if err := s.addFixedCommitteeRoot(period+1, common.Hash(bootstrap.CommitteeBranch[0])); err != nil {
-		s.Reset()
+		s.resetLocked()
 		return err
 	}
 	if err := s.addCommittee(period, bootstrap.Committee); err != nil {
-		s.Reset()
+		s.resetLocked()
 		return err
 	}
 	s.changeCounter++
```
