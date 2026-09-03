# [?] execution/vm: fix gas tracing underflow with EIP-8037 state gas (#20128)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-26
Source: https://github.com/erigontech/erigon/commit/b206fff09c1248eb07d252606431e4472f9d6136
Type: security-commit

## Details
execution/vm: fix gas tracing underflow with EIP-8037 state gas (#20128)

## Summary

Fixes #20086.

The tracing variable `cost` in the interpreter loop accumulated both
`dynamicCost.Regular` and `dynamicCost.State`, but `gasCopy` only
captured regular gas from `callContext.gas`. When `OnGasChange(gasCopy,
gasCopy-cost, ...)` was called for opcodes that charge state gas (e.g.
SSTORE creating a new slot, CREATE, CREATE2), the uint64 subtraction
underflowed — producing garbage values visible in
`debug_traceTransaction` and similar RPC methods.

**Fix:** Remove `cost += dynamicCost.State`. State gas is already
charged separately via `useMdGas()`, and `cost` is only used for
tracing, so it should only reflect regular gas to match `gasCopy`.

**Note:** State gas consumption events are intentionally suppressed via
`GasChangeIgnored`, pending a spec for multi-dimensional gas tracing.
The `useMdGas()` infrastructure already accepts tracer/reason
parameters, so adding state gas tracing events in the future is
straightforward.

### Changes
- `execution/vm/interpreter.go`: Remove `cost += dynamicCost.State` (1
line), add clarifying comment
- `execution/vm/runtime/runtime_test.go`: Add
`TestGasTracingNoUnderflowOnStateGas` — executes SSTORE under Amsterdam
rules and verifies `OnGasChange` never produces underflowing values

## Test plan
- [x] `go test -short ./execution/vm/...` passes
- [x] `TestGasTracingNoUnderflowOnStateGas` verifies the fix
- [ ] CI lint + full test suite

🤖 Generated with [Claude Code](https://claude.com/claude-code)


_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/b206fff09c1248eb07d252606431e4472f9d6136_
