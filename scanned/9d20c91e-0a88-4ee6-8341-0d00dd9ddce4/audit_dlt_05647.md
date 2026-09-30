# [?] [SharovBot] Fix data race between buildFiles and recalcVisibleFiles (#19590)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-04
Source: https://github.com/erigontech/erigon/commit/2db714813b45b85ec07c22d8460ca9f670b36b4c
Type: security-commit

## Details
[SharovBot] Fix data race between buildFiles and recalcVisibleFiles (#19590)

**[SharovBot]** Fix DATA RACE in `db/state/aggregator.go`

## Summary
- `buildFiles()` calls `BeginFilesRo()` on `Domain` and `InvertedIndex`
without holding `visibleFilesLock`, racing with `recalcVisibleFiles()`
which writes `_visible`/`_visibleFiles` fields under the same lock
- Wraps the `BeginFilesRo()` calls in `buildFiles()` with
`a.visibleFilesLock.RLock()`/`RUnlock()` to synchronize with the writer,
matching the pattern already used in `Aggregator.BeginFilesRo()`

## Test plan
- [x] `go build ./...` passes
- [x] `go test -race ./execution/verify/... -run
TestHistoryVerification_WithUserTransactions` passes 3 consecutive times
with no DATA RACE
- [x] `go test -race ./db/state/...` passes with no DATA RACE

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### db/state/aggregator.go
```diff
@@ -768,15 +768,17 @@ func (a *Aggregator) buildFiles(ctx context.Context, step kv.Step) error {
 
 	g, ctx := errgroup.WithContext(ctx)
 	g.SetLimit(a.collateAndBuildWorkers)
-	for _, d := range a.d {
+
+	// Use agg.BeginFilesRo() to safely snapshot visible files under visibleFilesLock,
+	// instead of calling individual domain/ii BeginFilesRo() without synchronization.
+	ac := a.BeginFilesRo()
+	for id, d := range a.d {
 		if d.Disable {
 			continue
 		}
 
 		d := d
-		dc := d.BeginFilesRo()
-		firstStepNotInFiles := dc.FirstStepNotInFiles()
-		dc.Close()
+		firstStepNotInFiles := ac.d[id].FirstStepNotInFiles()
 		if step < firstStepNotInFiles {
 			continue
 		}
@@ -820,9 +822,7 @@ func (a *Aggregator) buildFiles(ctx context.Context, step kv.Step) error {
 		}
 
 		ii := ii
-		dc := ii.BeginFilesRo()
-		firstStepNotInFiles := dc.FirstStepNotInFiles()
-		dc.Close()
+		firstStepNotInFiles := ac.iis[iikey].FirstStepNotInFiles()
 		if step < firstStepNotInFiles {
 			continue
 		}
@@ -849,6 +849,7 @@ func (a *Aggregator) buildFiles(ctx context.Context, step kv.Step) error {
 			return nil
 		})
 	}
+	ac.Close()
 	if err := g.Wait(); err != nil {
 		static.CleanupOnError()
 		return fmt.Errorf("domain collate-build: %w", err)
```
