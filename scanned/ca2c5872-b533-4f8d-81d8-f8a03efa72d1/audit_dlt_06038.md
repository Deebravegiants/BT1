# [?] fix(factory): recover panics while validating a proposed block (#4920)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2026-07-13
Source: https://github.com/iotexproject/iotex-core/commit/457ddbb390449703edb710fa45a16ec11c9eccb7
Type: security-commit

## Details
fix(factory): recover panics while validating a proposed block (#4920)

#4840 recovers panics on the mint path so a doomed draft cannot crash
the process. A proposed block is likewise untrusted input: extend the
same resilience to ValidateBlock so a panic while processing a block's
actions is recovered and surfaced as an error (the block is rejected)
instead of taking the validating node down. The working set is discarded
by the caller on error, so no partial state leaks and no committed state
changes; the commit/PutBlock path stays fatal as before.

Adds a regression test.

Co-authored-by: qevan <448293+guo@users.noreply.github.com>
