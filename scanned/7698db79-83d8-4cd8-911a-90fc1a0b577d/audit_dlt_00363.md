# [?] [vm] Iterative Drop for nested Move values (security fix) (#415)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-24
Source: https://github.com/aptos-labs/aptos-core/commit/d0d10695c5df010fb632762f700b770e064b7fe2
Type: security-commit

## Details
[vm] Iterative Drop for nested Move values (security fix) (#415)

* [vm] Iterative Drop for nested Move values

Deeply-nested Move values (long chains of nested structs) previously
overflowed the Rust stack when dropped via compiler-generated recursive
Drop, crashing the validator with SIGABRT.

Wraps the three recursive Container variants (Locals, Vec, Struct) in
a NestedValues newtype whose custom Drop walks nested containers via a
heap work-stack instead of Rust recursion. The inner Vec<Value> is
drained in place via Rc::get_mut so no sentinel Rc is ever allocated,
and the work stack only allocates when nested work is actually queued.

Includes a regression test that previously SIGABRT'd on a small thread
stack; now cleanly fails with VM_MAX_VALUE_DEPTH_REACHED.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* Address review comments

- into_rc: use ManuallyDrop + ptr::read to skip the sentinel Rc allocation
  (george)
- NestedValues::drop: exhaustive match on Value and Container (george)
- NestedValues::drop: vec![] nit (george)
- PoC test: assert Keep(MiscellaneousError(VM_MAX_VALUE_DEPTH_REACHED))
  and fail on thread panic (bugbot + george)
- PoC test: spell out 512 KB (was mis-parenthesized as 2*1024*1024/4),
  explain that both module count (10 vs 40) and exec thread stack size
  (512KB vs 2MB) are downsized 4x to keep the test fast while preserving
  the overflow shape (bugbot + user)
- PoC test: drop commented-out gas-schedule block (george)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
