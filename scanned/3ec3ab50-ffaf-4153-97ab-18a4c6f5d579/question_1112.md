# Q1112: debt-remove-scaled via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) in a state where it count one deposit as backing for two simultaneous claims? Given that it clears the debt bit only when the remaining scaled debt is exactly zero, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `ft` trait principal varied, and assert that the value `debt-remove-scaled` returns is identical in both runs; a divergence confirms the finding.
