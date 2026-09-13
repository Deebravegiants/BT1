# [?] node/app/event: fix data race on eventBus.prevQueueSize (#21551)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-03
Source: https://github.com/erigontech/erigon/commit/e7f75c9a700fbcd60b1d1394ec9e109c0cf5cc43
Type: security-commit

## Details
node/app/event: fix data race on eventBus.prevQueueSize (#21551)

## Summary

`eventBus.prevQueueSize` gates a debug-logging heuristic (the "Execpool
overflowing / recovering" messages), but it was read
(`eventbus.go:185`/`192`) and written (`eventbus.go:201`) without
synchronization while multiple async `Publish` goroutines run
concurrently. The race detector flags this. It's harmless to correctness
(logging only), but a genuine data race — fixed by making the field an
`atomic.Int64`.

## Context

Surfaced while investigating the disabled `node/app/component` test
package (whose `TestMain` does `os.Exit(0)`, so none of its tests run).
Re-enabling that package under `-race` flagged this race first. It's
split out here as a focused, independently-reviewable fix.

The remaining problems that keep the component package disabled —
cross-test event-subscription leakage and ~400 leaked actor goroutines
that deadlock the suite — are **not** addressed here and are tracked in
#21552.

## Testing

- `go build ./node/app/...` — clean
- `node/app/event` passes `go test -race -count=5`
- `make lint` — clean

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
