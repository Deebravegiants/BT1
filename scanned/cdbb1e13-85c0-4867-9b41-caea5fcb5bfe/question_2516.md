# Q2516: call-liquidate via liquidate: credit one side of an accounting pair without the other

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `call-liquidate` (mainnet/contracts/market/v0-4-market.clar:907) in a state where it credit one side of an accounting pair without the other? Given that it invokes `liquidate` with `none` for price-feeds, so a whole batch shares one snapshot, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:907` -> `call-liquidate`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `call-liquidate` invokes `liquidate` with `none` for price-feeds, so a whole batch shares one snapshot. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `collateral-receiver` varied, and assert that the value `call-liquidate` returns is identical in both runs; a divergence confirms the finding.
