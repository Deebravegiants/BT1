# [?] [vm] Prevent Display recursion stack overflow on deep Values (security fix) (#427) (#19774)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-05-15
Source: https://github.com/aptos-labs/aptos-core/commit/a21a09960bc0aec97689458feee8e5d2d1822fcc
Type: security-commit

## Details
[vm] Prevent Display recursion stack overflow on deep Values (security fix) (#427) (#19774)

* [vm] Gate state dump on enable_debugging (security fix)

The interpreter's attach_state_if_invariant_violation walks every
local and operand-stack Value via Display when an InvariantViolation
fires. Display for Container recurses without depth bound, and a
deeply nested Value (e.g., a long chain of nested structs built via
Pack on user-published modules) overflows the executor thread's
2 MiB Rust stack, aborting the validator process with SIGABRT.

The dump is purely a diagnostic affordance. Gate the entire branch
on vm_config.enable_debugging -- production validators run with this
flag off (DEBUGGING_ENABLED.get().unwrap_or(false) in
prod_configs.rs), so the user-controlled attack surface is closed on
mainnet. The aptos-debugger and any dev tool that calls
set_debugging_enabled(true) still gets the full dump.

No consensus impact: the dump only ever flows into VMError.message,
which is dropped on the way to TransactionStatus for
InvariantViolation paths -- KeptVMStatus::MiscellaneousError carries
no message field, From<KeptVMStatus> for ExecutionStatus discards
the message via `message: _` on the ExecutionFailure arm, and
TransactionAuxiliaryData::detail_error_message is #[serde(skip)] in
TransactionOutput. Nothing reachable from internal_state_str's
output enters the BCS-hashed TransactionInfo, so the gate is safe
to roll out asymmetrically across the validator set.

Includes a regression test that mirrors the iterative-Drop PoC:
builds a 10,000-deep Value, then triggers TOO_MANY_TYPE_NODES via
borrow_global<W> on a wide-W resource (931 layout nodes > 512). On
a 512 KB exec thread, the pre-fix path SIGABRTs from Display
recursion inside the dump path; the fix produces
Keep(MiscellaneousError(Some(VERIFICATION_ERROR))).



* [vm] Cap Display recursion depth on Value (security fix)

_Trimmed to 38 lines — full report: https://github.com/aptos-labs/aptos-core/commit/a21a09960bc0aec97689458feee8e5d2d1822fcc_
