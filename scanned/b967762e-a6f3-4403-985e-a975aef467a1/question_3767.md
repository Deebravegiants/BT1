# Q3767: status-multi via collateral-add: count one deposit as backing for two simultaneous claims

## Question
`status-multi` (mainnet/contracts/registry/v0-assets.clar:163) calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing `amount`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:163` -> `status-multi`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `status-multi` calls `(map unwrap-status ids mask)` as a TWO-LIST map where `mask` is `uint-to-list-u64` of the bitmap, pairing each id positionally and truncating to the shorter list. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
