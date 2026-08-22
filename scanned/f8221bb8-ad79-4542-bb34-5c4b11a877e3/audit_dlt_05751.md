# [?] [execution] Fix BlockExecutor panic during state sync abort (#19268)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-02
Source: https://github.com/aptos-labs/aptos-core/commit/4f190a1292b6d3c05a31a593d498c36306370ae5
Type: security-commit

## Details
[execution] Fix BlockExecutor panic during state sync abort (#19268)

When state sync aborts the consensus pipeline, `finish()` sets
`inner = None`. But `spawn_blocking` tasks that can't be cancelled
may still call `pre_commit_block` or `commit_ledger`, hitting
`.expect("BlockExecutor is not reset")` and panicking the validator.

Replace the two `.expect()` calls with `.ok_or_else()` to return
an error instead, consistent with how `ledger_update` already
handles this case.

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
