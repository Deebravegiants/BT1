# [?] Fix data race in TxPool.Stop from duplicate shutdown calls (#1111)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2026-08-05
Source: https://github.com/0xsoniclabs/sonic/commit/e95c9e9549f3ea7f5ac7abbdd8b374c403987e31
Type: security-commit

## Details
Fix data race in TxPool.Stop from duplicate shutdown calls (#1111)

* Fix data race in TxPool.Stop from duplicate shutdown calls

TxPool.Stop() could be invoked concurrently: once via gossip.Service's
node lifecycle shutdown, and once via config.MakeNode's cleanup chain.
Both paths raced on the unguarded txJournal.writer field. Guard Stop()
with sync.Once so it's safe to call more than once.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

* Use structured log

---------

Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>
