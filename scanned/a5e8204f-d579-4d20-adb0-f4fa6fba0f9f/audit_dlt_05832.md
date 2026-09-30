# [?] Bump TRACE_STATE_SHADOW_*_LIMIT_FACTORs by 10x to avoid exhaustion (#1581)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2025-08-08
Source: https://github.com/stellar/rs-soroban-env/commit/c92809c746b4f8ea6eb1b18dd49e5c7e2718c9cb
Type: security-commit

## Details
Bump TRACE_STATE_SHADOW_*_LIMIT_FACTORs by 10x to avoid exhaustion (#1581)

Part of https://github.com/stellar/rs-soroban-env/issues/1578 --
diagnostic events were being eaten in trace mode due to exhaustion of
shadow budget.

## Patch
### soroban-env-host/src/host/trace.rs
```diff
@@ -17,8 +17,8 @@ mod fmt;
 // than normal; not so high that it will run forever but high enough that we can manage
 // to actually record the quantity of detail that tracing records (eg. hashing everything
 // in the host on every host function call and return!).
-const TRACE_STATE_SHADOW_CPU_LIMIT_FACTOR: u64 = 500;
-const TRACE_STATE_SHADOW_MEM_LIMIT_FACTOR: u64 = 30;
+const TRACE_STATE_SHADOW_CPU_LIMIT_FACTOR: u64 = 5000;
+const TRACE_STATE_SHADOW_MEM_LIMIT_FACTOR: u64 = 300;
 
 pub type TraceHook = Rc<dyn for<'a> Fn(&'a Host, TraceEvent<'a>) -> Result<(), HostError>>;
 
```
