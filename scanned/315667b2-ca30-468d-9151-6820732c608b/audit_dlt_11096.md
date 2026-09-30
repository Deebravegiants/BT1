# [?] op-node/p2p/sync: add panic guard (#10611)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-05-22
Source: https://github.com/bobanetwork/boba/commit/94b97363f2fd98929ae6abe33dda09970c909c6f
Type: security-commit

## Details
op-node/p2p/sync: add panic guard (#10611)

* op-node/p2p/sync add panic guard

* hoist panic guard up to entire doRequest method

* panicGuard uses currying

* remove unecessary wrapper method

* fix test to use more accurate fn signature

remove unecessary assertion, this was annoying the linter

## Patch
### op-node/p2p/sync.go
```diff
@@ -573,7 +573,7 @@ func (s *SyncClient) peerLoop(ctx context.Context, id peer.ID) {
 			start := time.Now()
 
 			resultCode := ResultCodeSuccess
-			err := s.doRequest(ctx, id, pr.num)
+			err := panicGuard(s.doRequest)(ctx, id, pr.num)
 			if err != nil {
 				s.inFlight.delete(pr.num)
 				log.Warn("failed p2p sync request", "num", pr.num, "err", err)
@@ -657,36 +657,24 @@ func (s *SyncClient) doRequest(ctx context.Context, id peer.ID, expectedBlockNum
 	if _, err := io.ReadFull(r, versionData[:]); err != nil {
 		return fmt.Errorf("failed to read version part of response: %w", err)
 	}
-	version := binary.LittleEndian.Uint32(versionData[:])
-	if version != 0 && version != 1 {
-		return fmt.Errorf("unrecognized version: %d", version)
-	}
+
 	// payload is SSZ encoded with Snappy framed compression
 	r = snappy.NewReader(r)
 	r = io.LimitReader(r, maxGossipSize)
+
 	// We cannot stream straight into the SSZ decoder, since we need the scope of the SSZ payload.
 	// The server does not prepend it, nor would we trust a claimed length anyway, so we buffer the data we get.
 	data, err := io.ReadAll(r)
 	if err != nil {
 		return fmt.Errorf("failed to read response: %w", err)
 	}
 
-	envelope := &eth.ExecutionPayloadEnvelope{}
-
-	if version == 0 {
-		expectedBlockTime := s.cfg.TimestampForBlock(expectedBlockNum)
-		envelope, err = s.readExecutionPayload(data, expectedBlockTime)
-		if err != nil {
-			return err
-		}
-	} else if version == 1 {
-		if err := envelope.UnmarshalSSZ(uint32(len(data)), bytes.NewReader(data)); err != nil {
-			return fmt.Errorf("failed to decode execution payload envelope response: %w", err)
-		}
-	} else {
-		panic(fmt.Errorf("should have already filtered by version, but got: %d", version))
+	version := binary.LittleEndian.Uint32(versionData[:])
+	isCanyon := s.cfg.IsCanyon(s.cfg.TimestampForBlock(expectedBlockNum))
+	envelope, err := readExecutionPayload(version, data, isCanyon)
+	if err != nil {
+		return err
 	}
-
 	if err := str.CloseRead(); err != nil {
 		return fmt.Errorf("failed to close reading side")
 	}
@@ -701,18 +689,41 @@ func (s *SyncClient) doRequest(ctx context.Context, id peer.ID, expectedBlockNum
 	return nil
 }
 
-func (s *SyncClient) readExecutionPayload(data []byte, expectedTime uint64) (*eth.ExecutionPayloadEnvelope, error) {
-	blockVersion := eth.BlockV1
-	if s.cfg.IsCanyon(expectedTime) {
-		blockVersion = eth.BlockV2
+// panicGuard is a generic function that takes another function with generic arguments and returns an error.
+// It recovers from any panic that occurs during the execution of the function.
+func panicGuard[T, S, U any](fn func(T, S, U) error) func(T, S, U) error {
+	return func(arg0 T, arg1 S, arg2 U) (err error) {
+		defer func() {
+			if r := recover(); r != nil {
+				err = fmt.Errorf("recovered from a panic: %v", r)
+			}
+		}()
+		return fn(arg0, arg1, arg2)
 	}
+}
 
-	var res eth.ExecutionPayload
-	if err := res.UnmarshalSSZ(blockVersion, uint32(len(data)), bytes.NewReader(data)); err != nil {
-		return nil, fmt.Errorf("failed to decode response: %w", err)
+// readExecutionPayload will unmarshal the supplied data into an ExecutionPayloadEnvelope.
+func readExecutionPayload(version uint32, data []byte, isCanyon bool) (*eth.ExecutionPayloadEnvelope, error) {
+	switch version {
+	case 0:
+		blockVersion := eth.BlockV1
+		if isCanyon {
+			blockVersion = eth.BlockV2
+		}
+		var res eth.ExecutionPayload
+		if err := res.UnmarshalSSZ(blockVersion, uint32(len(data)), bytes.NewReader(data)); err != nil {
+			return nil, fmt.Errorf("failed to decode response: %w", err)
+		}
+		return &eth.ExecutionPayloadEnvelope{ExecutionPayload: &res}, nil
+	case 1:
+		envelope := &eth.ExecutionPayloadEnvelope{}
+		if err := envelope.UnmarshalSSZ(uint32(len(data)), bytes.NewReader(data)); err != nil {
+			return nil, fmt.Errorf("failed to decode execution payload envelope response: %w", err)
+		}
+		return envelope, nil
+	default:
+		return nil, fmt.Errorf("unrecognized version: %d", version)
 	}
-
-	return &eth.ExecutionPayloadEnvelope{ExecutionPayload: &res}, nil
 }
 
 func verifyBlock(envelope *eth.ExecutionPayloadEnvelope, expectedNum uint64) error {
```

### op-node/p2p/sync_test.go
```diff
@@ -391,3 +391,14 @@ func TestNetworkNotifyAddPeerAndRemovePeer(t *testing.T) {
 	_, peerBExist3 := syncCl.peers[hostB.ID()]
 	require.True(t, !peerBExist3, "peerB should not exist in syncClient")
 }
+
+func TestPanicGuard(t *testing.T) {
+	mockPanickingFn := func(ctx context.Context, id peer.ID, expectedBlockNum uint64) error {
+		panic("gotcha")
+	}
+	require.NotPanics(t, func() {
+		err := panicGuard(mockPanickingFn)(context.Background(), peer.ID(""), 37)
+		require.EqualError(t, err, "recovered from a panic: gotcha")
+	})
+
+}
```
