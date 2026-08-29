# Q5858: accrue-user-collateral via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the vault whose share price the redemption moves, can an unprivileged attacker make `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) count one deposit as backing for two simultaneous claims? `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the vault whose share price the redemption moves varied, and assert that the value `accrue-user-collateral` returns is identical in both runs; a divergence confirms the finding.
