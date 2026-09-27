# [?] fix(spice): avoid panic when re-endorsing a chunk certified on another fork (#15909)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-06-15
Source: https://github.com/near/nearcore/commit/fd672206c21f26269a9bf1bdcc0efdeb4cc4170d
Type: security-commit

## Details
fix(spice): avoid panic when re-endorsing a chunk certified on another fork (#15909)

`record_block_core_statements` panicked with "for each endorsement we
should save corresponding uncertified execution result" when a block's
endorsement core statements re-crossed the endorsement threshold for a
chunk whose execution result was already certified.

Certification is recorded in the fork-agnostic `execution_results`
column (keyed only by the endorsed chunk), while `uncertified_chunks` is
ancestry-relative, so a producer building on a branch that lacks the
certifying block legitimately re-emits the endorsement core statements.
If the node had certified that chunk via a `ChunkExecutionResult` core
statement on another fork (which never populates
`uncertified_execution_results`), re-deriving the endorsed state
demanded an uncertified result that was never stored, and the
`.expect()` panicked.

Skip the chunk when its result is already present in
`execution_results`: there is nothing to materialize. Adds a regression
test that certifies a chunk on one fork and re-emits a sub-threshold
endorsement on a sibling fork.
