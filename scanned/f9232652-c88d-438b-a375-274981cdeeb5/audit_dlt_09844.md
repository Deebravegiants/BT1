# [?] fix nil pointer crash when counting one bit in onNewView

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-06-09
Source: https://github.com/harmony-one/harmony/commit/e38a33b2f25080bd515511ddb0ff5e6624936e2d
Type: security-commit

## Details
fix nil pointer crash when counting one bit in onNewView

## Patch
### consensus/view_change.go
```diff
@@ -392,13 +392,14 @@ func (consensus *Consensus) onNewView(msg *msg_pb.Message) {
 	}
 
 	if err = verifyMessageSig(senderKey, msg); err != nil {
-		utils.GetLogInstance().Debug("onNewView failed to verify new leader's signature", "error", err)
+		utils.GetLogInstance().Error("onNewView failed to verify new leader's signature", "error", err)
 		return
 	}
 	consensus.vcLock.Lock()
 	defer consensus.vcLock.Unlock()
 
-	if recvMsg.M3AggSig == nil {
+	if recvMsg.M3AggSig == nil || recvMsg.M3Bitmap == nil {
+		utils.GetLogInstance().Error("onNewView M3AggSig or M3Bitmap is nil")
 		return
 	}
 	m3Sig := recvMsg.M3AggSig
```

### internal/utils/bytes.go
```diff
@@ -90,6 +90,9 @@ func countOneBitsInByte(by byte) int {
 
 // CountOneBits counts the number of 1 bit in byte array
 func CountOneBits(arr []byte) int {
+	if len(arr) == 0 {
+		return 0
+	}
 	count := 0
 	for i := range arr {
 		count += countOneBitsInByte(arr[i])
```
