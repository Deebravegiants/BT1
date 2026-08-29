# Q1766: get-cached-indexes via repay: record a repayment larger than the value actually delivere

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling the `ft` trait principal, can an unprivileged attacker make `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) record a repayment larger than the value actually delivered? `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with the `ft` trait principal varied, and assert that the value `get-cached-indexes` returns is identical in both runs; a divergence confirms the finding.
