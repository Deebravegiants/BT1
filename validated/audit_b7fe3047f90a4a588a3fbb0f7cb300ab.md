Looking at the bug class carefully: **per-input validation that doesn't account for accumulated state**, where a per-operation check is bypassed by transferring "identity" between operations. I need to find an analog in cb-mpc where a per-contribution check exists but cumulative state isn't validated.

Let me examine the TDH2 `combine_additive` function and the `rid` field more carefully.