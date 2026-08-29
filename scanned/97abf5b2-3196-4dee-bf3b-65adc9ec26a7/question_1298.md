# Q1298: merge-price via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling the zToken/underlying id mapping reached (the u100 sentinel branch), can an unprivileged attacker make `merge-price` (mainnet/contracts/market/v0-4-market.clar:506) record a repayment larger than the value actually delivered? `merge-price` attaches a price to an asset record by position in the fold, not by asset id, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:506` -> `merge-price`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `merge-price` attaches a price to an asset record by position in the fold, not by asset id. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with the zToken/underlying id mapping reached (the u100 sentinel branch) varied, and assert that the value `merge-price` returns is identical in both runs; a divergence confirms the finding.
