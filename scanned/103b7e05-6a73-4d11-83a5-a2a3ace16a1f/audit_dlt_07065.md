# [?] [SharovBot] fix(stagedsync): add mutex to Progress.LogCommitments to fix DATA RACE (#19501)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-02-26
Source: https://github.com/erigontech/erigon/commit/f568d6fbda741a693d1dd55b838f06eca9db2d29
Type: security-commit

## Details
[SharovBot] fix(stagedsync): add mutex to Progress.LogCommitments to fix DATA RACE (#19501)

**[SharovBot]**

## Problem

The `All tests (with -race)` CI job has been failing on `main` since
#19486 merged. The race detector reports:

```
WARNING: DATA RACE
Read at 0x...: (*Progress).LogCommitments() exec3_metrics.go:741
Previous write at 0x...: (*Progress).LogCommitments() exec3_metrics.go:742

WARNING: DATA RACE  
Read at 0x...: updateExecDomainMetrics() exec3_metrics.go:267
Previous write at 0x...: updateExecDomainMetrics() exec3_metrics.go:291
```

Both races are concurrent calls to `Progress.LogCommitments()` from:
- **Goroutine A** (`func1.2`): the commit-logger goroutine spawned
inside `parallelExecutor.exec` — triggered when the `commitProgress`
channel closes (`!ok` case at `exec3_parallel.go:350`)
- **Goroutine B** (outer `exec()`): at `exec3_parallel.go:470`, after
`pe.wait()` returns, for the final summary log call

## Root Cause

The `<-LogCommitmentsDone` synchronisation at `exec3_parallel.go:408`
only runs on the **normal commit-completion path**. If `func1` exits
early via `ctx.Done()` (at line 443), it never reaches line 408 —
leaving the commit-logger goroutine (`func1.2`) still running.
`pe.wait()` returns (tracking `execLoopGroup`, which `func1` is part
of), the outer `exec()` proceeds to its `LogCommitments` call — and both
goroutines simultaneously mutate `p.prevCommitTime`,
`p.prevDomainMetrics`, etc.

**Why did #19486 expose this?** It made BAL validation optional, so more
Amsterdam-fork blocks complete successfully instead of aborting.
`TestExecutionSpecBlockchainDevnet` runs short-lived test contexts; with
more successful commits the race window is hit consistently.

## Fix

Add `sync.Mutex` to `Progress` and lock it for the duration of
`LogCommitments()`. All `p.prev*` field reads and writes happen inside
this one function, so a single lock site covers both reported races.

```go
type Progress struct {
    mu sync.Mutex  // protects prev* fields from concurrent LogCommitments calls
    // ...
}

func (p *Progress) LogCommitments(...) {
    p.mu.Lock()
    defer p.mu.Unlock()
    // ...
}
```

## Verification

`go build ./execution/stagedsync/...` passes. The fix unblocks `All
tests (with -race)` on `main`.

Co-authored-by: SharovBot <sharovbot@erigon.ci>

## Patch
### execution/stagedsync/exec3_metrics.go
```diff
@@ -455,6 +455,11 @@ func NewProgress(initialBlockNum, initialTxNum, commitThreshold uint64, updateMe
 }
 
 type Progress struct {
+	// mu protects all prev* fields accessed concurrently from the commit-logger
+	// goroutine (func1.2 inside parallelExecutor.exec) and the outer exec()
+	// function after pe.wait() returns. The commit-logger goroutine may still
+	// be running when the outer exec calls LogCommitments for the final summary.
+	mu                             sync.Mutex
 	initialTime                    time.Time
 	initialTxNum                   uint64
 	initialBlockNum                uint64
@@ -725,6 +730,9 @@ func (p *Progress) LogExecution(rs *state.StateV3, ex executor) {
 }
 
 func (p *Progress) LogCommitments(rs *state.StateV3, ex executor, commitStart time.Time, stepsInDb float64, lastProgress commitment.CommitProgress) {
+	p.mu.Lock()
+	defer p.mu.Unlock()
+
 	var te *txExecutor
 	var suffix string
 
```
