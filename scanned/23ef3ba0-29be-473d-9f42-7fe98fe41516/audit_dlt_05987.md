# [?] Fix deadlock in commit_blocks: drop block MutexGuards before prune()

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-03-14
Source: https://github.com/Conflux-Chain/conflux-rust/commit/4d049f4d3d64a5d3c1fa238e46a77a096b11430e
Type: security-commit

## Details
Fix deadlock in commit_blocks: drop block MutexGuards before prune()

The removal of the `for block in blocks { state_tree().prune() }` loop
left the `blocks` Vec<MutexGuard<SpeculationBlock>> alive when
`db_with_cache.prune()` was called. Since prune() tries to re-lock the
same blocks via get_block(), this caused a mutex deadlock that made the
node hang during PoS genesis bootstrap.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
