# [?] webrtc: fix deadlock on connection close (#2580)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2023-09-25
Source: https://github.com/libp2p/go-libp2p/commit/785684f42793d1f51c3e2d1c9b2399deb47ff00b
Type: security-commit

## Details
webrtc: fix deadlock on connection close (#2580)

## Patch
### p2p/transport/webrtc/stream.go
```diff
@@ -123,7 +123,23 @@ func newStream(
 			}
 		}
 
-		s.maybeDeclareStreamDone()
+		if s.isDone() {
+			// onDone removes the stream from the connection and requires the connection lock.
+			// This callback(onBufferedAmountLow) is executing in the sctp readLoop goroutine.
+			// If Connection.Close is called concurrently, the closing goroutine will acquire
+			// the connection lock and wait for sctp readLoop to exit, the sctp readLoop will
+			// wait for the connection lock before exiting, causing a deadlock.
+			// Run this in a different goroutine to avoid the deadlock.
+			go func() {
+				s.mx.Lock()
+				defer s.mx.Unlock()
+				// TODO: we should be closing the underlying datachannel, but this resets the stream
+				// See https://github.com/libp2p/specs/issues/575 for details.
+				// _ = s.dataChannel.Close()
+				// TODO: write for the spawned reader to return
+				s.onDone()
+			}()
+		}
 
 		select {
 		case s.writeAvailable <- struct{}{}:
@@ -186,11 +202,10 @@ func (s *stream) processIncomingFlag(flag *pb.Message_Flag) {
 	s.maybeDeclareStreamDone()
 }
 
-// this is used to force reset a stream
+// maybeDeclareStreamDone is used to force reset a stream. It should be called with
+// the stream lock acquired. It calls stream.onDone which requires the connection lock.
 func (s *stream) maybeDeclareStreamDone() {
-	if (s.sendState == sendStateReset || s.sendState == sendStateDataSent) &&
-		(s.receiveState == receiveStateReset || s.receiveState == receiveStateDataRead) &&
-		len(s.controlMsgQueue) == 0 {
+	if s.isDone() {
 		_ = s.SetReadDeadline(time.Now().Add(-1 * time.Hour)) // pion ignores zero times
 		// TODO: we should be closing the underlying datachannel, but this resets the stream
 		// See https://github.com/libp2p/specs/issues/575 for details.
@@ -200,6 +215,14 @@ func (s *stream) maybeDeclareStreamDone() {
 	}
 }
 
+// isDone indicates whether the stream is completed and all the control messages have also been
+// flushed. It must be called with the stream lock acquired.
+func (s *stream) isDone() bool {
+	return (s.sendState == sendStateReset || s.sendState == sendStateDataSent) &&
+		(s.receiveState == receiveStateReset || s.receiveState == receiveStateDataRead) &&
+		len(s.controlMsgQueue) == 0
+}
+
 func (s *stream) setCloseError(e error) {
 	s.mx.Lock()
 	defer s.mx.Unlock()
```
