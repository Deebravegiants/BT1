# Q3872: user-safe-mask via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls which collateral and debt asset pair is targeted reach `user-safe-mask` (mainnet/contracts/market/v0-4-market.clar:428) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:428` -> `user-safe-mask`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `user-safe-mask` ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with which collateral and debt asset pair is targeted varied, and assert that the value `user-safe-mask` returns is identical in both runs; a divergence confirms the finding.
