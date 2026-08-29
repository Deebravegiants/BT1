# [?] [SharovBot] fix: data race on DelayLoggingEnabled - use atomic.Bool (#23107)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-08-07
Source: https://github.com/erigontech/erigon/commit/ede5bb0853a3cbf0e4f28015875af48aa41bf95a
Type: security-commit

## Details
[SharovBot] fix: data race on DelayLoggingEnabled - use atomic.Bool (#23107)

**[SharovBot]**

## Problem

DATA RACE detected in TestImportClosesChaindataOnInitError (CI run:
https://github.com/erigontech/erigon/actions/runs/31190048942/job/92904328219):

Two goroutines concurrently access the global DelayLoggingEnabled bool
variable:
- Writer: SetupLoggerCtx() sets it from the CLI flag
(node/logging/logging.go:68)
- Reader: UpdateBlockConsumer*Delay() functions read it on every block
event (execution/metrics/block.go:80)

## Fix

Replace the plain bool with sync/atomic.Bool:
- All reads use .Load()
- The single write uses .Store()

No behavior change — atomic.Bool zero-value is false, same as before.

## Testing

- go vet ./execution/metrics/... ./node/logging/... passes
- No test files modified

Co-authored-by: SharovBot <sharovbot@erigon.ci>
Co-authored-by: Giulio Rebuffo <giulio.rebuffo@gmail.com>
