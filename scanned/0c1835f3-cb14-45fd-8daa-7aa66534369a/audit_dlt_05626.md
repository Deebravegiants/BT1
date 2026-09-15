# [?] [SharovBot] fix: track MergeLoop goroutine in bgComponentsEg to prevent data race on shutdown (#22244)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-05
Source: https://github.com/erigontech/erigon/commit/deca4190ce499fec595f46befc679389ac9e4cee
Type: security-commit

## Details
[SharovBot] fix: track MergeLoop goroutine in bgComponentsEg to prevent data race on shutdown (#22244)

**[SharovBot]**

## Problem

A data race was detected in `TestImportClosesChaindataOnInitError`
(race-tests CI job, 2026-07-03):

```
WARNING: DATA RACE
Write at 0x00c0653acb90 by goroutine 321:
  github.com/erigontech/erigon/db/state.(*Aggregator).Close()
      db/state/aggregator.go:630

Previous read at 0x00c0653acb90 by goroutine 373:
  github.com/erigontech/erigon/db/state.(*Aggregator).MergeLoop()
      db/state/aggregator.go:1228
  github.com/erigontech/erigon/node/eth.New.func16()
      node/eth/backend.go:1133
```

## Context

PR #22203 (merged 2026-07-04) addressed this race by replacing
`sync.WaitGroup` with a `closingWaitGroup` latch in `Aggregator`, making
`MergeLoop`'s `TryAdd()` properly ordered against `Close()`'s
`BeginClose()+Wait()`.

## This PR

This PR provides an additional, complementary fix: track the MergeLoop
goroutine in `bgComponentsEg` so `Stop()` → `bgComponentsEg.Wait()`
explicitly waits for the MergeLoop goroutine to exit before
`chainDB.Close()` is called.

Without this, `bgComponentsEg.Wait()` in `Stop()` returns without
waiting for the MergeLoop goroutine (since it was launched as a bare `go
func()`), meaning the goroutine could theoretically still be running
when `chainDB.Close()` begins. The `closingWaitGroup` handles the
WaitGroup reuse race, but this PR makes the shutdown ordering explicit
and unambiguous.

**Changes:**
- Moves the MergeLoop goroutine from a bare `go func()` to
`backend.bgComponentsEg.Go()`
- Fixes the typo: `"snapashot"` → `"snapshot"` in the error message
- Filters context cancellation errors (expected on shutdown) from
`logger.Error`

## Testing

- `go test -race -count=10 ./cmd/utils/app/ -run
TestImportClosesChaindataOnInitError` — all 10 runs PASS, no data race
- `go build ./...` — succeeds
- No test files modified

Fixes CI:
https://github.com/erigontech/erigon/actions/runs/28674562917/job/85045122311

Co-authored-by: SharovBot <sharovbot@erigon.tech>
Co-authored-by: Giulio Rebuffo <giulio.rebuffo@gmail.com>

### node/eth/backend.go
```diff
@@ -1129,11 +1129,17 @@ func New(ctx context.Context, stack *node.Node, config *ethconfig.Config, logger
 	}
 
 	if !dbg.NoBackgroundMaintenance() {
-		go func() {
-			if err := temporalDb.Debug().MergeLoop(ctx); err != nil {
-				logger.Error("snapashot merge loop error", "err", err)
+		// Track the MergeLoop goroutine in bgComponentsEg so that Stop() →
+		// bgComponentsEg.Wait() waits for it to exit before chainDB.Close().
+		// Without this, there is a data race between the goroutine reading
+		// Aggregator fields (in wg.TryAdd) and Close() writing them after
+		// wg.Wait() returns.
+		backend.bgComponentsEg.Go(func() error {
+			if err := temporalDb.Debug().MergeLoop(ctx); err != nil && !errors.Is(err, context.Canceled) {
+				logger.Error("snapshot merge loop error", "err", err)
 			}
-		}()
+			return nil
+		})
 	}
 
 	return backend, nil
```
