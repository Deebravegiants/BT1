# [?] fix: data race in getMinGasPrice via LastBlockHeight (#7102)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-04-17
Source: https://github.com/celestiaorg/celestia-app/commit/33942ca0a4afe720ecca6bd3e5323ad3173a9ccc
Type: security-commit

## Details
fix: data race in getMinGasPrice via LastBlockHeight (#7102)

## Summary

- Replaces `app.CreateQueryContext(app.LastBlockHeight(), false)` with
`app.CreateQueryContext(0, false)` in `getMinGasPrice` and
`getGovMaxSquareBytes` to avoid a data race against concurrent block
commits.

## Why

`BaseApp.LastBlockHeight()` reads `rootmulti.Store.lastCommitInfo`
without taking `checkStateMu`, so it races with
`rootmulti.Store.Commit()` which writes that field. This caused flaky
`test-race` failures in `pkg/user/v2/TestV2SubmitMethods` (the
gas-estimation gRPC handler called `getMinGasPrice` concurrently with
block commits).


[celestiaorg/cosmos-sdk#715](https://github.com/celestiaorg/cosmos-sdk/pull/715)
(picked up in #7037) already widened `checkStateMu` to cover `Commit`
and the `LatestVersion()` read inside `CreateQueryContext` — but
`BaseApp.LastBlockHeight()` sits outside that protection. Passing `0` to
`CreateQueryContext` routes the height read through the race-safe
`LatestVersion()` path under `checkStateMu.RLock`.

Semantically equivalent to "query at latest committed height," just
race-free.

## Test plan

- [x] `make build` succeeds
- [x] `go test -race -v -count=10 -run TestV2SubmitMethods
./pkg/user/v2/` — no `WARNING: DATA RACE` in 10 runs
- [ ] CI `test-race` passes

Closes #7101

🤖 Generated with [Claude Code](https://claude.com/claude-code)
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/celestiaorg/celestia-app/pull/7102"
target="_blank">
  <picture>
<source media="(prefers-color-scheme: dark)"
srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
<img
src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1"
alt="Open with Devin">
  </picture>
</a>
<!-- devin-review-badge-end -->

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### app/app.go
```diff
@@ -798,7 +798,11 @@ func (app *App) RegisterTxService(clientCtx client.Context) {
 }
 
 func (app *App) getGovMaxSquareBytes() (uint64, error) {
-	ctx, err := app.CreateQueryContext(app.LastBlockHeight(), false)
+	// Pass height 0 so CreateQueryContext reads the latest committed height under
+	// checkStateMu.RLock. Calling app.LastBlockHeight() here would race with
+	// concurrent block commits because BaseApp.LastBlockHeight reads
+	// rootmulti.Store.lastCommitInfo without taking the lock.
+	ctx, err := app.CreateQueryContext(0, false)
 	if err != nil {
 		return 0, err
 	}
@@ -813,7 +817,11 @@ func (app *App) getMinGasPrice() (float64, error) {
 	if err != nil {
 		localMinGasPrice = appconsts.DefaultMinGasPrice
 	}
-	ctx, err := app.CreateQueryContext(app.LastBlockHeight(), false)
+	// Pass height 0 so CreateQueryContext reads the latest committed height under
+	// checkStateMu.RLock. Calling app.LastBlockHeight() here would race with
+	// concurrent block commits because BaseApp.LastBlockHeight reads
+	// rootmulti.Store.lastCommitInfo without taking the lock.
+	ctx, err := app.CreateQueryContext(0, false)
 	if err != nil {
 		return localMinGasPrice, err
 	}
```
