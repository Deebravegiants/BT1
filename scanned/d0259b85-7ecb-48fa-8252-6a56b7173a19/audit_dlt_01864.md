# [?] fix(op-interop-filter): prevent uint64 underflow in calculateStartingBlock (#19720)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-23
Source: https://github.com/ethereum-optimism/optimism/commit/e7b34fe3fb664cc4b1bbdbfa4602b99fb1fa843e
Type: security-commit

## Details
fix(op-interop-filter): prevent uint64 underflow in calculateStartingBlock (#19720)

When startTimestamp < backfillDuration.Seconds(), the subtraction wraps
around to a large uint64 value. Guard against this by checking before
subtracting and falling back to genesis block.

Fixes runtimeverification/_audits_Ethereum-optimism_optimism_interopv2#37

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
