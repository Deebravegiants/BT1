# [?] db/kv/mdbx: fix deadlock in async tx channel on context cancellation (#19856)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-13
Source: https://github.com/erigontech/erigon/commit/2b495bb1bc750c45fa732ca650e73b22b51adc80
Type: security-commit

## Details
db/kv/mdbx: fix deadlock in async tx channel on context cancellation (#19856)

## Summary

- Fix deadlock in `asyncTx.Apply()`, `asyncRwTx.Apply()`, and
`asyncRwTx.ApplyRw()` where unbuffered error channels (`make(chan
error)`) cause the MDBX goroutine to block forever if the caller's
context is cancelled before reading the result
- Change all three channels to buffered (`make(chan error, 1)`) so the
send always succeeds even if nobody reads

## Background

The MDBX async transaction methods use a pattern where the caller sends
work to a goroutine locked to an OS thread, then waits on both the
result channel and the context. If the context fires first, the caller
returns `ctx.Err()` and nobody reads from `rc`. The MDBX goroutine then
blocks forever on `a.err <- result`, permanently deadlocking the write
thread.

This was observed as a **14-hour stall** on a mainnet parallel execution
node where the MDBX write thread was stuck sending to an abandoned
channel.

## Test plan

- [x] Verified the change is limited to channel buffer size (no logic
changes)
- [ ] CI passes (`make lint && make erigon integration`)
- [ ] Mainnet parallel execution node runs without stalling

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Mark Holt <erigon@dev-bm-e3-ethmainnet-n4.erigon.io>
Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
