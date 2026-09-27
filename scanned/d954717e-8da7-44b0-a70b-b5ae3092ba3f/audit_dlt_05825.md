# [?] fix: spice: Do not crash when accessing debug info. (#14454)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-10-16
Source: https://github.com/near/nearcore/commit/f1d30b5353b01dd56da11d3a6193ca0fb31eb2ab
Type: security-commit

## Details
fix: spice: Do not crash when accessing debug info. (#14454)

In spice prev_state_root isn't part of chunks and we have debug_assert
false when accessing it (which is best to keep in place to catch any
unexpected and significant access points that need fixing).
