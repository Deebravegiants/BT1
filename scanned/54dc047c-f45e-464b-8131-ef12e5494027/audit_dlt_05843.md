# [?] fix!: sealer: handle initialisation error without panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2024-07-15
Source: https://github.com/filecoin-project/lotus/commit/85587dd5b412a3570a1d51f3df1ca8e8a340970d
Type: security-commit

## Details
fix!: sealer: handle initialisation error without panic

storage/pipeline.NewPreCommitBatcher and storage/pipeline.New now have an additional
error return to deal with errors arising from fetching the sealing config.

## Patch
### itests/api_test.go
```diff
@@ -173,6 +173,8 @@ func (ts *apiSuite) testOutOfGasError(t *testing.T) {
 		buildconstants.BlockGasLimit = originalLimit
 	}()
 
+	t.Logf("BlockGasLimit changed: %d", buildconstants.BlockGasLimit)
+
 	msg := &types.Message{
 		From:  senderAddr,
 		To:    senderAddr,
@@ -289,6 +291,7 @@ func (ts *apiSuite) testNonGenesisMiner(t *testing.T) {
 	ctx := context.Background()
 
 	full, genesisMiner, ens := kit.EnsembleMinimal(t, append(ts.opts, kit.MockProofs())...)
+
 	ens.InterconnectAll().BeginMining(4 * time.Millisecond)
 
 	time.Sleep(1 * time.Second)
```

### node/modules/storageminer.go
```diff
@@ -255,7 +255,10 @@ func SealingPipeline(fc config.MinerFeeConfig) func(params SealingPipelineParams
 		provingBuffer := md.WPoStProvingPeriod * 2
 		pcp := sealing.NewBasicPreCommitPolicy(api, gsd, provingBuffer)
 
-		pipeline := sealing.New(ctx, api, fc, evts, maddr, ds, sealer, verif, prover, &pcp, gsd, j, as)
+		pipeline, err := sealing.New(ctx, api, fc, evts, maddr, ds, sealer, verif, prover, &pcp, gsd, j, as)
+		if err != nil {
+			return nil, xerrors.Errorf("creating sealing pipeline: %w", err)
+		}
 
 		lc.Append(fx.Hook{
 			OnStart: func(context.Context) error {
```

### storage/pipeline/precommit_batch.go
```diff
@@ -67,7 +67,7 @@ type PreCommitBatcher struct {
 	lk                    sync.Mutex
 }
 
-func NewPreCommitBatcher(mctx context.Context, maddr address.Address, api PreCommitBatcherApi, addrSel AddressSelector, feeCfg config.MinerFeeConfig, getConfig dtypes.GetSealingConfigFunc) *PreCommitBatcher {
+func NewPreCommitBatcher(mctx context.Context, maddr address.Address, api PreCommitBatcherApi, addrSel AddressSelector, feeCfg config.MinerFeeConfig, getConfig dtypes.GetSealingConfigFunc) (*PreCommitBatcher, error) {
 	b := &PreCommitBatcher{
 		api:       api,
 		maddr:     maddr,
@@ -86,20 +86,20 @@ func NewPreCommitBatcher(mctx context.Context, maddr address.Address, api PreCom
 		stopped: make(chan struct{}),
 	}
 
-	go b.run()
+	cfg, err := b.getConfig()
+	if err != nil {
+		return nil, xerrors.Errorf("failed to get sealer config: %w", err)
+	}
+
+	go b.run(cfg)
 
-	return b
+	return b, nil
 }
 
-func (b *PreCommitBatcher) run() {
+func (b *PreCommitBatcher) run(cfg sealiface.Config) {
 	var forceRes chan []sealiface.PreCommitBatchRes
 	var lastRes []sealiface.PreCommitBatchRes
 
-	cfg, err := b.getConfig()
-	if err != nil {
-		panic(err)
-	}
-
 	timer := time.NewTimer(b.batchWait(cfg.PreCommitBatchWait, cfg.PreCommitBatchSlack))
 	for {
 		if forceRes != nil {
```

### storage/pipeline/sealing.go
```diff
@@ -230,7 +230,7 @@ type pendingPiece struct {
 	accepted func(abi.SectorNumber, abi.UnpaddedPieceSize, error)
 }
 
-func New(mctx context.Context, sapi SealingAPI, fc config.MinerFeeConfig, events Events, maddr address.Address, ds datastore.Batching, sealer sealer.SectorManager, verif storiface.Verifier, prov storiface.Prover, pcp PreCommitPolicy, gc dtypes.GetSealingConfigFunc, journal journal.Journal, addrSel AddressSelector) *Sealing {
+func New(mctx context.Context, sapi SealingAPI, fc config.MinerFeeConfig, events Events, maddr address.Address, ds datastore.Batching, sealer sealer.SectorManager, verif storiface.Verifier, prov storiface.Prover, pcp PreCommitPolicy, gc dtypes.GetSealingConfigFunc, journal journal.Journal, addrSel AddressSelector) (*Sealing, error) {
 	s := &Sealing{
 		Api:      sapi,
 		DealInfo: &CurrentDealInfoManager{sapi},
@@ -257,9 +257,8 @@ func New(mctx context.Context, sapi SealingAPI, fc config.MinerFeeConfig, events
 
 		addrSel: addrSel,
 
-		terminator:  NewTerminationBatcher(mctx, maddr, sapi, addrSel, fc, gc),
-		precommiter: NewPreCommitBatcher(mctx, maddr, sapi, addrSel, fc, gc),
-		commiter:    NewCommitBatcher(mctx, maddr, sapi, addrSel, fc, gc, prov),
+		terminator: NewTerminationBatcher(mctx, maddr, sapi, addrSel, fc, gc),
+		commiter:   NewCommitBatcher(mctx, maddr, sapi, addrSel, fc, gc, prov),
 
 		getConfig: gc,
 
@@ -270,6 +269,11 @@ func New(mctx context.Context, sapi SealingAPI, fc config.MinerFeeConfig, events
 			byState:  map[SectorState]int64{},
 		},
 	}
+	pc, err := NewPreCommitBatcher(mctx, maddr, sapi, addrSel, fc, gc)
+	if err != nil {
+		return nil, err
+	}
+	s.precommiter = pc
 
 	s.notifee = func(before, after SectorInfo) {
 		s.journal.RecordEvent(s.sealingEvtType, func() interface{} {
@@ -287,7 +291,7 @@ func New(mctx context.Context, sapi SealingAPI, fc config.MinerFeeConfig, events
 
 	s.sectors = statemachine.New(namespace.Wrap(ds, datastore.NewKey(SectorStorePrefix)), s, SectorInfo{})
 
-	return s
+	return s, nil
 }
 
 func (m *Sealing) Run(ctx context.Context) {
```
