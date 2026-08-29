# Q3104: calc-liq-debt-repay via liquidate-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the vault whose share price the redemption moves reach `calc-liq-debt-repay` (mainnet/contracts/market/v0-4-market.clar:723) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it takes the liquidation factor times the debt with `mul-bps-down`, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:723` -> `calc-liq-debt-repay`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `calc-liq-debt-repay` takes the liquidation factor times the debt with `mul-bps-down`. Reach it through `liquidate-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the vault whose share price the redemption moves varied, and assert that the value `calc-liq-debt-repay` returns is identical in both runs; a divergence confirms the finding.
