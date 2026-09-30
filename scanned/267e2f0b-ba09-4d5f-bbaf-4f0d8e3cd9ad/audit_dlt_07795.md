# [?] Fix get RANDAO endpoint for underflow (#11650)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2022-11-11
Source: https://github.com/OffchainLabs/prysm/commit/bf7e17db8f9c34545d291dadfb566a2b2654a33e
Type: security-commit

## Details
Fix get RANDAO endpoint for underflow (#11650)

* Fix get randao end point for underflow

* Fix test

## Patch
### beacon-chain/rpc/eth/beacon/state.go
```diff
@@ -152,8 +152,14 @@ func (bs *Server) GetRandao(ctx context.Context, req *eth2.RandaoRequest) (*eth2
 	if req.Epoch != nil {
 		epoch = *req.Epoch
 	}
-	// future epochs and epochs too far back are not supported
-	if epoch > stEpoch || uint64(epoch) < uint64(stEpoch)-uint64(st.RandaoMixesLength())+1 {
+
+	// future epochs and epochs too far back are not supported.
+	randaoEpochLowerBound := uint64(0)
+	// Lower bound should not underflow.
+	if uint64(stEpoch) > uint64(st.RandaoMixesLength()) {
+		randaoEpochLowerBound = uint64(stEpoch) - uint64(st.RandaoMixesLength())
+	}
+	if epoch > stEpoch || uint64(epoch) < randaoEpochLowerBound+1 {
 		return nil, status.Errorf(codes.InvalidArgument, "Epoch is out of range for the randao mixes of the state")
 	}
 	idx := epoch % params.BeaconConfig().EpochsPerHistoricalVector
```

### beacon-chain/rpc/eth/beacon/state_test.go
```diff
@@ -272,6 +272,13 @@ func TestGetRandao(t *testing.T) {
 	require.NoError(t, st.UpdateRandaoMixesAtIndex(uint64(epochCurrent%params.BeaconConfig().EpochsPerHistoricalVector), mixCurrent))
 	require.NoError(t, st.UpdateRandaoMixesAtIndex(uint64(epochOld%params.BeaconConfig().EpochsPerHistoricalVector), mixOld))
 
+	headEpoch := types.Epoch(1)
+	headSt, err := util.NewBeaconState()
+	require.NoError(t, err)
+	require.NoError(t, headSt.SetSlot(params.BeaconConfig().SlotsPerEpoch))
+	headRandao := bytesutil.PadTo([]byte("head"), 32)
+	require.NoError(t, headSt.UpdateRandaoMixesAtIndex(uint64(headEpoch), headRandao))
+
 	db := dbTest.SetupDB(t)
 	chainService := &chainMock.ChainService{}
 	server := &Server{
@@ -298,6 +305,14 @@ func TestGetRandao(t *testing.T) {
 		require.NoError(t, err)
 		assert.DeepEqual(t, mixOld, resp.Data.Randao)
 	})
+	t.Run("head state below `EpochsPerHistoricalVector`", func(t *testing.T) {
+		server.StateFetcher = &testutil.MockFetcher{
+			BeaconState: headSt,
+		}
+		resp, err := server.GetRandao(ctx, &eth2.RandaoRequest{StateId: []byte("head")})
+		require.NoError(t, err)
+		assert.DeepEqual(t, headRandao, resp.Data.Randao)
+	})
 	t.Run("epoch too old", func(t *testing.T) {
 		epochTooOld := types.Epoch(100000 - st.RandaoMixesLength())
 		_, err := server.GetRandao(ctx, &eth2.RandaoRequest{StateId: make([]byte, 0), Epoch: &epochTooOld})
```
