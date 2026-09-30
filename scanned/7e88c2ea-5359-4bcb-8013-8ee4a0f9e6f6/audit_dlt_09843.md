# [?] [crash] fix invalid memory access crash

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-06-09
Source: https://github.com/harmony-one/harmony/commit/e606983608c4c55dc8fae89ac46c4142069da27d
Type: security-commit

## Details
[crash] fix invalid memory access crash

Signed-off-by: Leo Chen <leo@harmony.one>

## Patch
### consensus/view_change.go
```diff
@@ -426,6 +426,11 @@ func (consensus *Consensus) onNewView(msg *msg_pb.Message) {
 		}
 	}
 
+	if m3Mask.Bitmap == nil || m2Mask.Bitmap == nil {
+		utils.GetLogInstance().Error("onNewView m3Mask or m2Mask is nil")
+		return
+	}
+
 	// check when M3 sigs > M2 sigs, then M1 (recvMsg.Payload) should not be empty
 	if utils.CountOneBits(m3Mask.Bitmap) > utils.CountOneBits(m2Mask.Bitmap) {
 		if len(recvMsg.Payload) <= 32 {
```
