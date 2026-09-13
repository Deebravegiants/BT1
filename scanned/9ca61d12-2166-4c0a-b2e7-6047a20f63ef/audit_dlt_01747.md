# [?] fix: don't overflow when token supply is close to u128::MAX (#14170)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-09-03
Source: https://github.com/near/nearcore/commit/d45f06876662c6676d947d22ab3a20c99a300962
Type: security-commit

## Details
fix: don't overflow when token supply is close to u128::MAX (#14170)

One of issues we've hit during testing [#releases/2.8 > 2.8 @
💬](https://near.zulipchat.com/#narrow/channel/522473-releases.2F2.2E8/topic/2.2E8/near/537292816).
There are spontaneous stake tx from mainnet validators which we don't
clean up properly; for now we ignore them by multiplying all stakes by
10**5. This, however, brings token supply closer to `u128::MAX`. This,
in turn, breaks all formulas of kind `stake * a / b` where `a / b <= 1`.

We could try `stake / b * a`, but I guess using `U256` is safer and
shouldn't really slow down the chain.
