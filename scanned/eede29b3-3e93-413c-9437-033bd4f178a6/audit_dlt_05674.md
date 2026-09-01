# [?] core, blockstm, state, docs: harden valuesEqual, recover validation panic, split settleNonces/settleStorage, document tx lifecycle

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2026-05-13
Source: https://github.com/0xPolygon/bor/commit/6cbd6ffbe3a1dcf862c3172e381958de18b5f1f1
Type: security-commit

## Details
core, blockstm, state, docs: harden valuesEqual, recover validation panic, split settleNonces/settleStorage, document tx lifecycle

- core/state/parallel_statedb_validate.go: replace `default: a == b` in
  valuesEqual with an explicit type switch over the MVStore value types
  in use (bool, uint64, common.Hash, []byte, nil). Unknown types now
  panic with a clear message instead of either silently degrading to
  pointer-identity (for pointer types) or crashing the runtime (for
  non-comparable types like slices, maps, or structs containing them) —
  both of which would be consensus-affecting failure modes the moment a
  new MVStore subpath is added.

- core/blockstm/v2_executor.go: wrap runValidationLoop's body in a
  defer-recover so a panic in Validate() is captured into
  V2ExecutionResult.ValidationPanic instead of crashing the bor process
  via an unrecovered goroutine panic. A second deferred close on
  chSettle (guarded by settleClosed) keeps the settle goroutine from
  hanging on wg.Wait when the recover path skips the normal cleanup.
  core/parallel_state_processor.go: surface a non-nil ValidationPanic
  as an error so BlockChain.ProcessBlock falls back to the serial
  processor instead of taking down the node.

- core/state/parallel_statedb_settle.go: split settleNoncesAndStorage
  into settleNonces and settleStorage. The two loops were independent
  with no shared state or ordering constraint; bundling them was
  inconsistent with the rest of the per-concern settle helpers. Test
  TestPDB_SettleNoncesAndStorage splits in lockstep.

- docs/blockstm-v2.md: add a Transaction Lifecycle section between
  Execution Flow and Key data structures. Covers (1) the state diagram
  a tx passes through, (2) the structural invariant that bounds each
  tx to at most two executions (validation order + the
  finishReexec(i-1) gate + no re-validation of the re-exec result),
  (3) a worked cascading-vfail example walking tx1/tx2/tx3 through
  initial+reexec to show why a 3-tx cascade still converges with one
  re-exec per failed tx, and (4) a concurrency timeline diagram
  illustrating the worker/validator/reexec/settle lanes. Also reorders
  the Storage/Nonces bullets in the Settlement section to match
  SettleTo's call order.

_Trimmed to 38 lines — full report: https://github.com/0xPolygon/bor/commit/6cbd6ffbe3a1dcf862c3172e381958de18b5f1f1_
