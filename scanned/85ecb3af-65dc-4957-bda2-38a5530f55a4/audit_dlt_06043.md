# [?] vm: fix data race on CallTracer interruptReason

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-25
Source: https://github.com/kaiachain/kaia/commit/0a29eb48a894cd5b3dcb255d21c408e81216b9c9
Type: security-commit

## Details
vm: fix data race on CallTracer interruptReason

Stop() (timeout goroutine) and GetResult() (main goroutine) accessed
interruptReason concurrently with no happens-before edge. Write the reason
before the release Store in Stop(), and read it in GetResult() only after
an acquire interrupt.Load().

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
