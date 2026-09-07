# [?] Enforce `DepthLimiter` in the `Host` to avoid stack overflow (#904)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2023-07-14
Source: https://github.com/stellar/rs-soroban-env/commit/63e8430b0efd6c8a96134f2d6dc22d615e05bbc0
Type: security-commit

## Details
Enforce `DepthLimiter` in the `Host` to avoid stack overflow (#904)

* Enforce `DepthLimiter` on `Env` to avoid stack overflow

* fixup! Enforce `DepthLimiter` on `Env` to avoid stack overflow

* Remove `DepthGuard`; Remove `EnvBase` dependency on `DepthLimiter`; clean-ups

* Revert unintentional touch

* Refresh xdr
