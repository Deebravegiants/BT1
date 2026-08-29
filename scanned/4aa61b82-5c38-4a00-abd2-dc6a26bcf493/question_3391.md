# Q3391: convert-to-scaled-debt via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
`convert-to-scaled-debt` (mainnet/contracts/market/v0-4-market.clar:648) scales a token amount by the cached borrow index, rounding up on the borrow path. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the redemption receiver, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:648` -> `convert-to-scaled-debt`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the redemption receiver, then read `convert-to-scaled-debt` state before and after in the same block and assert the two sides of the invariant are equal.
