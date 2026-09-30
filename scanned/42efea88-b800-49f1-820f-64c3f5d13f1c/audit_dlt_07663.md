# [?] Fix panic on `GetEthV1BeaconBlobs` (#17992)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-11-21
Source: https://github.com/erigontech/erigon/commit/01573fdbc1ad45ff67e69001ce2d9a2b91e13e00
Type: security-commit

## Details
Fix panic on `GetEthV1BeaconBlobs` (#17992)

closes https://github.com/erigontech/erigon/issues/17990

## Patch
### cl/beacon/handler/handler.go
```diff
@@ -150,6 +150,7 @@ func NewApiHandler(
 	builderClient builder.BuilderClient,
 	caplinStateSnapshots *snapshotsync.CaplinStateSnapshots,
 	enableMemoizedHeadState bool,
+	peerDas das.PeerDas,
 ) *ApiHandler {
 	blobBundles, err := lru.New[common.Bytes48, BlobBundle]("blobs", maxBlobBundleCacheSize)
 	if err != nil {
@@ -174,6 +175,7 @@ func NewApiHandler(
 		syncedData:                         syncedData,
 		stateReader:                        stateReader,
 		caplinStateSnapshots:               caplinStateSnapshots,
+		peerDas:                            peerDas,
 		slotWaitedForAttestationProduction: slotWaitedForAttestationProduction,
 		randaoMixesPool: sync.Pool{New: func() interface{} {
 			return solid.NewHashVector(int(beaconChainConfig.EpochsPerHistoricalVector))
```

### cl/beacon/handler/utils_test.go
```diff
@@ -178,6 +178,7 @@ func setupTestingHandler(t *testing.T, v clparams.StateVersion, logger log.Logge
 		nil,
 		nil,
 		false,
+		nil,
 	) // TODO: add tests
 	h.Init()
 	return
```

### cl/beacon/handler/validator_test.go
```diff
@@ -77,6 +77,7 @@ func (t *validatorTestSuite) SetupTest() {
 		nil,
 		nil,
 		false,
+		nil,
 	)
 	t.gomockCtrl = gomockCtrl
 }
```

### cmd/caplin/caplin1/run.go
```diff
@@ -453,6 +453,7 @@ func RunCaplinService(ctx context.Context, engine execution_client.ExecutionEngi
 			option.builderClient,
 			stateSnapshots,
 			true,
+			peerDas,
 		)
 		go beacon.ListenAndServe(&beacon.LayeredBeaconHandler{
 			ArchiveApi: apiHandler,
```
