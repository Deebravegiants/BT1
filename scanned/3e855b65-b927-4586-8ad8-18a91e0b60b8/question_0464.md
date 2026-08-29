# Q0464: calc-liquidation-params via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `calc-liquidation-params` (mainnet/contracts/market/v0-4-market.clar:739) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:739` -> `calc-liquidation-params`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `calc-liquidation-params` chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `calc-liquidation-params` returns is identical in both runs; a divergence confirms the finding.
