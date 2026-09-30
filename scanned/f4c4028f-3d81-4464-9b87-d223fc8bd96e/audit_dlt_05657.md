# [?] Fix data race on s.head.full in postPayloadTasks (#16839)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-05-27
Source: https://github.com/OffchainLabs/prysm/commit/5b44483086f0331c1d5647cba196947ba493607a
Type: security-commit

## Details
Fix data race on s.head.full in postPayloadTasks (#16839)

- `s.head.full = true` written with no lock — races with `setHead` and
RLock readers
- Take `headLock.Lock()` and re-check `s.head.root == root` before
mutating

## Patch
### beacon-chain/blockchain/receive_execution_payload_envelope.go
```diff
@@ -153,9 +153,11 @@ func (s *Service) postPayloadTasks(ctx context.Context, envelope interfaces.ROEx
 	}
 	blockHash := bytesutil.ToBytes32(payload.BlockHash())
 
-	if s.head != nil {
+	s.headLock.Lock()
+	if s.head != nil && s.head.root == root {
 		s.head.full = true
 	}
+	s.headLock.Unlock()
 
 	attr := s.getPayloadAttribute(ctx, st, envelope.Slot()+1, headRoot[:], true)
 	if s.inRegularSync() {
```

### changelog/terence_fix-head-full-data-race.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Protect `s.head.full` write in `postPayloadTasks` with `headLock` to avoid a data race with `setHead` and concurrent readers.
```
