# Q2072: calc-utilization via liquidate-multi: credit one side of an accounting pair without the other

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls how many entries share one price snapshot (price-feeds is passed as none) reach `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) in a state where it credit one side of an accounting pair without the other? Given that it divides debt by available liquidity, which can exceed BPS when debt outruns assets, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `liquidate-multi` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with how many entries share one price snapshot (price-feeds is passed as none) varied, and assert that the value `calc-utilization` returns is identical in both runs; a divergence confirms the finding.
