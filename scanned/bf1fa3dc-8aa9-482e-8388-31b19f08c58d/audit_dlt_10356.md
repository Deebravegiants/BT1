# [?] avoid crash on empty data

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2021-01-12
Source: https://github.com/0xsoniclabs/sonic/commit/cbe8d6b2cd556bab9cd95c9b3908938f47ff1052
Type: security-commit

## Details
avoid crash on empty data

## Patch
### gossip/handler_fuzz.go
```diff
@@ -110,6 +110,10 @@ type fuzzMsgReadWriter struct {
 }
 
 func newFuzzMsg(data []byte) (*p2p.Msg, error) {
+	if len(data) < 1 {
+		return nil, ErrEmptyMessage
+	}
+
 	var (
 		codes = []uint64{
 			EthStatusMsg,
```
