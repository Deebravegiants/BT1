# [?] fix(spice): execution results race condition (#14953)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-02-03
Source: https://github.com/near/nearcore/commit/9c9c28f4dba386601276e207ac5bc64926ecfffc
Type: security-commit

## Details
fix(spice): execution results race condition (#14953)

I think there is a race condition with spice execution results:

`postprocess_ready_block`:
1. `record_uncertified_chunks_for_block` updates
`DBCol::uncertified_chunks` to reflect
which chunks were certified by this block's `ChunkExecutionResult` core
statements.
2. `check_orphans` runs immediately after - if an orphan child block
exists, it calls
`start_process_block_impl`, which calls
`get_last_certified_execution_results_for_next_block`.

That function needs the execution results for the last certified block.
It checks two places:
the store (`DBCol::execution_results`) and the current block's core
statements. But execution
results are only written to the store asynchronously. So neither source
has the data, and the lookup panics.

So I changed `get_last_certified_execution_results_for_next_block` to
look at parent blocks for the necessary results.
In most cases, this should be a short chain.
