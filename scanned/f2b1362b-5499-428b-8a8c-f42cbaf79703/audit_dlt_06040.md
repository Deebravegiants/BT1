# [?] fix(factory): recover mint goroutine panics to keep process alive (#4840)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2026-05-28
Source: https://github.com/iotexproject/iotex-core/commit/ed00eba013a106ef80870352cbe5c763a47a4562
Type: security-commit

## Details
fix(factory): recover mint goroutine panics to keep process alive (#4840)

When block-sync commits a block while a draft mint is in flight, the
trie's copy-on-write delete can remove a node that the mint goroutine
later traverses, surfacing as db.ErrNotExist inside EVM SetState. With
panicUnrecoverableError set after the Upernavik hardfork this crashes
the iotex-server process via log.Panic.

Wrap blockPreparer.prepare's mint goroutine with defer-recover so a
panicked draft is discarded and reported back to the caller as an
error instead of taking the process down. The recover is scoped to
this goroutine only -- the block-apply path (PutBlock) runs on a
different goroutine and remains fatal, preserving the corruption
safety net there.

Also adds an Error log with the panic value + stack and a Prometheus
counter (iotex_mint_panics_total) for operator visibility.

This is a hotfix. A follow-up will address the underlying race
(tip-change cancellation + mint-path db.ErrNotExist as hard abort).

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
Co-authored-by: CoderZhi <thecoderzhi@gmail.com>
