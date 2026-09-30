# [?] node/pkg/common: Fix race condition in PostObservationRequest

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2022-08-17
Source: https://github.com/wormhole-foundation/wormhole/commit/4712a6f774c9fec82be9ec4ccd82cb037161b691
Type: security-commit

## Details
node/pkg/common: Fix race condition in PostObservationRequest

Any goroutine can push into a channel so the current implementation has
a race condition where the channel can become full immediately after the
length check, causing the subsequent send on the channel to block.

Fix this by wrapping the send on the channel with a select block.
Control will fall through to the default case only if the actual send
operation blocks, avoiding the potential race with other goroutines.

## Patch
### node/pkg/common/obsvReqSendC.go
```diff
@@ -1,19 +1,20 @@
 package common
 
 import (
-	"fmt"
+	"errors"
 
 	gossipv1 "github.com/certusone/wormhole/node/pkg/proto/gossip/v1"
 )
 
 const ObsvReqChannelSize = 50
-const ObsvReqChannelFullError = "channel is full"
 
-func PostObservationRequest(obsvReqSendC chan *gossipv1.ObservationRequest, req *gossipv1.ObservationRequest) error {
-	if len(obsvReqSendC) >= cap(obsvReqSendC) {
-		return fmt.Errorf(ObsvReqChannelFullError)
-	}
+var ErrChanFull = errors.New("channel is full")
 
-	obsvReqSendC <- req
-	return nil
+func PostObservationRequest(obsvReqSendC chan<- *gossipv1.ObservationRequest, req *gossipv1.ObservationRequest) error {
+	select {
+	case obsvReqSendC <- req:
+		return nil
+	default:
+		return ErrChanFull
+	}
 }
```

### node/pkg/common/obsvReqSendC_test.go
```diff
@@ -30,8 +30,7 @@ func TestObsvReqSendLimitEnforced(t *testing.T) {
 			ChainId: uint32(vaa.ChainIDSolana),
 		}
 		err := PostObservationRequest(obsvReqSendC, req)
-		assert.NotNil(t, err)
-		assert.Equal(t, ObsvReqChannelFullError, err.Error())
+		assert.ErrorIs(t, err, ErrChanFull)
 
 		done = true
 	}()
```
