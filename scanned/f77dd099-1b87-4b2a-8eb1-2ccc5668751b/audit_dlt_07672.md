# [?] txnprovider/shutter: prevent panic in TestShutterBlockBuilding (#15792)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-06-27
Source: https://github.com/erigontech/erigon/commit/cee82f96d63042fdd4095040ccd369428369ac4b
Type: security-commit

## Details
txnprovider/shutter: prevent panic in TestShutterBlockBuilding (#15792)

relates to https://github.com/erigontech/erigon/issues/15775
first step, prevent the panic so we can see what the err is

## Patch
### txnprovider/shutter/internal/testhelpers/mock_cl.go
```diff
@@ -74,6 +74,9 @@ func (cl *MockCl) BuildBlock(ctx context.Context, opts ...BlockBuildingOption) (
 	// start block building process
 	fcuRes, err := retryEngineSyncing(ctx, func() (*enginetypes.ForkChoiceUpdatedResponse, enginetypes.EngineStatus, error) {
 		r, err := cl.engineApiClient.ForkchoiceUpdatedV3(ctx, &forkChoiceState, &payloadAttributes)
+		if err != nil {
+			return nil, "", err
+		}
 		return r, r.PayloadStatus.Status, err
 	})
 	if err != nil {
@@ -98,6 +101,9 @@ func (cl *MockCl) BuildBlock(ctx context.Context, opts ...BlockBuildingOption) (
 	// insert the newly built block
 	payloadStatus, err := retryEngineSyncing(ctx, func() (*enginetypes.PayloadStatus, enginetypes.EngineStatus, error) {
 		r, err := cl.engineApiClient.NewPayloadV4(ctx, payloadRes.ExecutionPayload, []common.Hash{}, &parentBeaconBlockRoot, []hexutil.Bytes{})
+		if err != nil {
+			return nil, "", err
+		}
 		return r, r.Status, err
 	})
 	if err != nil {
@@ -116,6 +122,9 @@ func (cl *MockCl) BuildBlock(ctx context.Context, opts ...BlockBuildingOption) (
 	}
 	fcuRes, err = retryEngineSyncing(ctx, func() (*enginetypes.ForkChoiceUpdatedResponse, enginetypes.EngineStatus, error) {
 		r, err := cl.engineApiClient.ForkchoiceUpdatedV3(ctx, &forkChoiceState, nil)
+		if err != nil {
+			return nil, "", err
+		}
 		return r, r.PayloadStatus.Status, err
 	})
 	if err != nil {
```
