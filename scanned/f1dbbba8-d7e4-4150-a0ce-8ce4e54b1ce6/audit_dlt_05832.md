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
