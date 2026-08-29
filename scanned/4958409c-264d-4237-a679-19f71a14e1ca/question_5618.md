# Q5618: find-asset via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the vault whose share price the redemption moves, can an unprivileged attacker make `find-asset` (mainnet/contracts/market/v0-4-market.clar:584) count one deposit as backing for two simultaneous claims? `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the vault whose share price the redemption moves varied, and assert that the value `find-asset` returns is identical in both runs; a divergence confirms the finding.
