# [?] Node/Gov: Fix panic in public RPC (#2601)

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2023-04-10
Source: https://github.com/wormhole-foundation/wormhole/commit/199159b5635b115cc337b63f4fb15ab2c3de7221
Type: security-commit

## Details
Node/Gov: Fix panic in public RPC (#2601)

* Node/Gov: Fix panic in public RPC

* governor: mitigate nil ptr deref

---------

Co-authored-by: Jeff Schroeder <jeffschroeder@computer.org>

## Patch
### node/pkg/governor/governor_monitoring.go
```diff
@@ -325,6 +325,10 @@ func (gov *ChainGovernor) IsVAAEnqueued(msgId *publicrpcv1.MessageID) (bool, err
 	gov.mutex.Lock()
 	defer gov.mutex.Unlock()
 
+	if msgId == nil {
+		return false, fmt.Errorf("no message ID specified")
+	}
+
 	emitterChain := vaa.ChainID(msgId.EmitterChain)
 
 	emitterAddress, err := vaa.StringToAddress(msgId.EmitterAddress)
```

### node/pkg/governor/governor_monitoring_test.go
```diff
@@ -0,0 +1,17 @@
+package governor
+
+import (
+	"testing"
+
+	"github.com/stretchr/testify/assert"
+	"github.com/test-go/testify/require"
+	"go.uber.org/zap"
+)
+
+func TestIsVAAEnqueuedNilMessageID(t *testing.T) {
+	logger, _ := zap.NewProduction()
+	gov := NewChainGovernor(logger, nil, GoTestMode)
+	enqueued, err := gov.IsVAAEnqueued(nil)
+	require.EqualError(t, err, "no message ID specified")
+	assert.Equal(t, false, enqueued)
+}
```

### node/pkg/publicrpc/publicrpcserver.go
```diff
@@ -157,6 +157,10 @@ func (s *PublicrpcServer) GovernorGetEnqueuedVAAs(ctx context.Context, req *publ
 func (s *PublicrpcServer) GovernorIsVAAEnqueued(ctx context.Context, req *publicrpcv1.GovernorIsVAAEnqueuedRequest) (*publicrpcv1.GovernorIsVAAEnqueuedResponse, error) {
 	resp := &publicrpcv1.GovernorIsVAAEnqueuedResponse{}
 
+	if req.MessageId == nil {
+		return nil, status.Error(codes.InvalidArgument, "no message ID specified")
+	}
+
 	if s.gov != nil {
 		var err error
 		resp.IsEnqueued, err = s.gov.IsVAAEnqueued(req.MessageId)
```

### node/pkg/publicrpc/publicrpcserver_test.go
```diff
@@ -4,6 +4,7 @@ import (
 	"context"
 	"testing"
 
+	"github.com/certusone/wormhole/node/pkg/governor"
 	publicrpcv1 "github.com/certusone/wormhole/node/pkg/proto/publicrpc/v1"
 	"github.com/stretchr/testify/assert"
 	"go.uber.org/zap"
@@ -63,3 +64,19 @@ func TestGetSignedVAABadAddress(t *testing.T) {
 	expected_err := status.Error(codes.InvalidArgument, "address must be 32 bytes")
 	assert.Equal(t, expected_err, err)
 }
+
+func TestGovernorIsVAAEnqueuedNoMessage(t *testing.T) {
+	ctx := context.Background()
+	logger, _ := zap.NewProduction()
+	gov := governor.NewChainGovernor(logger, nil, governor.GoTestMode)
+	server := &PublicrpcServer{logger: logger, gov: gov}
+
+	// A message without the messageId set should not panic but return an error instead.
+	msg := publicrpcv1.GovernorIsVAAEnqueuedRequest{}
+	assert.NotPanics(t, func() {
+		_, err := server.GovernorIsVAAEnqueued(ctx, &msg)
+		assert.Error(t, err)
+		expected_err := status.Error(codes.InvalidArgument, "no message ID specified")
+		assert.Equal(t, expected_err, err)
+	})
+}
```
