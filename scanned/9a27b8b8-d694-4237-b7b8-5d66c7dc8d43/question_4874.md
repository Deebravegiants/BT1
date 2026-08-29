# Q4874: relevant via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling how many entries share one price snapshot (price-feeds is passed as none), can an unprivileged attacker make `relevant` (mainnet/contracts/market/v0-market-vault.clar:175) destroy value through a truncation the opposite operation does not restore? `relevant` drops any position row whose bit is not present in the enabled mask, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with how many entries share one price snapshot (price-feeds is passed as none) varied, and assert that the value `relevant` returns is identical in both runs; a divergence confirms the finding.
