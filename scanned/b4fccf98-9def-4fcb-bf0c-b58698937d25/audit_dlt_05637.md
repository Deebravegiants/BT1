# [?] db/state: fix data race on Aggregator stepSize/stepsInFrozenFile (#20100)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-23
Source: https://github.com/erigontech/erigon/commit/2660b49705e5d69ed4d3510cf287696bb0b22173
Type: security-commit

## Details
db/state: fix data race on Aggregator stepSize/stepsInFrozenFile (#20100)

## Summary
- Convert `Aggregator.stepSize` and `Aggregator.stepsInFrozenFile` from
`uint64` to `atomic.Uint64`
- `ReloadErigonDBSettings()` writes these fields (from the staged sync
pipeline goroutine) while `MergeLoop` reads them concurrently via
`StepSize()`/`StepsInFrozenFile()`, causing a data race detected by the
race-tests CI shard
- All read sites use `.Load()`, all write sites use `.Store()`

## Test plan
- [x] `go build ./...` passes
- [x] `go test -short ./db/state/...` passes
- [x] `go test -run TestEngineApiBuiltBlockStateMatchesValidation
./execution/engineapi/` passes
- [ ] CI race-tests shard passes (was the failing check)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### db/state/aggregator.go
```diff
@@ -61,8 +61,8 @@ type Aggregator struct {
 	d                 [kv.DomainLen]*Domain
 	iis               []*InvertedIndex
 	dirs              datadir.Dirs
-	stepSize          uint64
-	stepsInFrozenFile uint64
+	stepSize          atomic.Uint64
+	stepsInFrozenFile atomic.Uint64
 	reorgBlockDepth   uint64
 
 	dirtyFilesLock           sync.Mutex
@@ -189,7 +189,7 @@ func (a *Aggregator) RegisterDomain(cfg statecfg.DomainCfg, salt *uint32, dirs d
 		cfg.Hist.HistoryDisabled = true
 		cfg.Hist.IiCfg.Disable = true
 	}
-	a.d[cfg.Name], err = NewDomain(cfg, a.stepSize, a.stepsInFrozenFile, dirs, logger)
+	a.d[cfg.Name], err = NewDomain(cfg, a.stepSize.Load(), a.stepsInFrozenFile.Load(), dirs, logger)
 	if err != nil {
 		return err
 	}
@@ -205,7 +205,7 @@ func (a *Aggregator) RegisterII(cfg statecfg.InvIdxCfg, salt *uint32, dirs datad
 	if a.disableHistory {
 		cfg.Disable = true
 	}
-	ii, err := NewInvertedIndex(cfg, a.stepSize, a.stepsInFrozenFile, dirs, logger)
+	ii, err := NewInvertedIndex(cfg, a.stepSize.Load(), a.stepsInFrozenFile.Load(), dirs, logger)
 	if err != nil {
 		return err
 	}
@@ -219,9 +219,9 @@ func (a *Aggregator) OnFilesChange(onChange, onDel kv.OnFilesChange) {
 	a.onFilesDelete = onDel
 }
 
-func (a *Aggregator) StepSize() uint64          { return a.stepSize }
+func (a *Aggregator) StepSize() uint64          { return a.stepSize.Load() }
 func (a *Aggregator) Dirs() datadir.Dirs        { return a.dirs }
-func (a *Aggregator) StepsInFrozenFile() uint64 { return a.stepsInFrozenFile }
+func (a *Aggregator) StepsInFrozenFile() uint64 { return a.stepsInFrozenFile.Load() }
 func (a *Aggregator) Logger() log.Logger        { return a.logger }
 
 func (a *Aggregator) ForTestReplaceKeysInValues(domain kv.Domain, v bool) {
@@ -258,30 +258,30 @@ func (a *Aggregator) reloadSalt() error {
 // If domains are already configured and stepSize changed, it propagates the new value to all
 // Domain/InvertedIndex instances.
 func (a *Aggregator) ReloadErigonDBSettings(noDownloader bool) error {
-	oldStepSize := a.stepSize
-	oldStepsInFrozenFile := a.stepsInFrozenFile
+	oldStepSize := a.stepSize.Load()
+	oldStepsInFrozenFile := a.stepsInFrozenFile.Load()
 
 	settings, err := ResolveErigonDBSettings(a.dirs, a.logger, noDownloader)
 	if err != nil {
 		return err
 	}
-	a.stepSize = settings.StepSize
-	a.stepsInFrozenFile = settings.StepsInFrozenFile
+	a.stepSize.Store(settings.StepSize)
+	a.stepsInFrozenFile.Store(settings.StepsInFrozenFile)
 
-	if a.configured && (a.stepSize != oldStepSize || a.stepsInFrozenFile != oldStepsInFrozenFile) {
+	if a.configured && (settings.StepSize != oldStepSize || settings.StepsInFrozenFile != oldStepsInFrozenFile) {
 		a.logger.Info("erigondb stepSize changed, propagating to domains/IIs",
-			"old_step_size", oldStepSize, "new_step_size", a.stepSize,
-			"old_steps_in_frozen_file", oldStepsInFrozenFile, "new_steps_in_frozen_file", a.stepsInFrozenFile)
+			"old_step_size", oldStepSize, "new_step_size", settings.StepSize,
+			"old_steps_in_frozen_file", oldStepsInFrozenFile, "new_steps_in_frozen_file", settings.StepsInFrozenFile)
 		// stepSize lives only on InvertedIndex; Domain and History access it through embedding.
 		// Update the InvertedIndex embedded in each domain's History, plus standalone IIs.
 		for _, d := range a.d {
 			if d != nil && d.History != nil && d.History.InvertedIndex != nil {
-				d.History.InvertedIndex.setStepSize(a.stepSize, a.stepsInFrozenFile)
+				d.History.InvertedIndex.setStepSize(settings.StepSize, settings.StepsInFrozenFile)
 			}
 		}
 		for _, ii := range a.iis {
 			if ii != nil {
-				ii.setStepSize(a.stepSize, a.stepsInFrozenFile)
+				ii.setStepSize(settings.StepSize, settings.StepsInFrozenFile)
 			}
 		}
 	}
@@ -294,7 +294,7 @@ func (a *Aggregator) ConfigureDomains() error {
 	if a.configured {
 		return nil
 	}
-	if a.stepSize == 0 {
+	if a.stepSize.Load() == 0 {
 		return fmt.Errorf("cannot configure domains: stepSize is 0")
 	}
 	// AdjustReceipt mutates the global statecfg.Schema; must run before Configure().
@@ -933,7 +933,7 @@ func (a *Aggregator) readyForCollation(ctx context.Context, step kv.Step) (lastB
 		return 0, 0, 0, true, nil
 	}
 	err = a.db.View(ctx, func(tx kv.Tx) error {
-		lastBlockInStep, ok, err = rawdbv3.TxNums.FindBlockNum(ctx, tx, lastTxNumOfStep(step, a.stepSize))
+		lastBlockInStep, ok, err = rawdbv3.TxNums.FindBlockNum(ctx, tx, lastTxNumOfStep(step, a.stepSize.Load()))
 		if err != nil {
 			return err
 		}
@@ -1801,7 +1801,7 @@ func (a *Aggregator) buildFilesInBackground(txNum uint64, doMerge bool) chan str
 		return fin
 	}
 
-	if (txNum + 1) <= a.visibleFilesMinimaxTxNum.Load()+a.stepSize {
+	if (txNum + 1) <= a.visibleFilesMinimaxTxNum.Load()+a.stepSize.Load() {
 		close(fin)
 		return fin
 	}
@@ -1983,7 +1983,7 @@ func (at *AggregatorRoTx) DomainProgress(name kv.Domain, tx kv.Tx) uint64 {
 		// this is not accurate, okay for reporting...
 		// if historyDisabled, there's no way to get progress in
 		// terms of exact txNum
-		return at.d[name].d.maxStepInDBNoHistory(tx).ToTxNum(at.a.stepSize)
+		return at.d[name].d.maxStepInDBNoHistory(tx).ToTxNum(at.a.stepSize.Load())
 	}
 	return at.d[name].ht.iit.Progress(tx)
 }
```

### db/state/aggregator2.go
```diff
@@ -65,8 +65,8 @@ func (opts AggOpts) Open(ctx context.Context, db kv.RoDB) (*Aggregator, error) {
 		return nil, err
 	}
 
-	a.stepSize = opts.stepSize
-	a.stepsInFrozenFile = opts.stepsInFrozenFile
+	a.stepSize.Store(opts.stepSize)
+	a.stepsInFrozenFile.Store(opts.stepsInFrozenFile)
 
 	a.disableHistory = opts.disableHistory
 	a.disableFsync = opts.disableFsync
```
