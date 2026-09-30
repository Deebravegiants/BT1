# [?] calling unlock using defer, preventing deadlock when miner.setEtherbase() returns an error

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2018-12-13
Source: https://github.com/Consensys-inc-archive/quorum/commit/aea11d53a8066fed2a1302394645d1a2a20d1a4e
Type: security-commit

## Details
calling unlock using defer, preventing deadlock when miner.setEtherbase() returns an error

## Patch
### eth/backend.go
```diff
@@ -356,12 +356,13 @@ func (s *Ethereum) Etherbase() (eb common.Address, err error) {
 // set in js console via admin interface or wrapper from cli flags
 func (s *Ethereum) SetEtherbase(etherbase common.Address) {
 	s.lock.Lock()
+	defer s.lock.Unlock()
 	if _, ok := s.engine.(consensus.Istanbul); ok {
 		log.Error("Cannot set etherbase in Istanbul consensus")
 		return
 	}
 	s.etherbase = etherbase
-	s.lock.Unlock()
+
 
 	s.miner.SetEtherbase(etherbase)
 }
```
