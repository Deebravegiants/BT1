# Q2300: calc-treasury-lp-preview via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the redemption receiver reach `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) in a state where it credit one side of an accounting pair without the other? Given that it divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the redemption receiver varied, and assert that the value `calc-treasury-lp-preview` returns is identical in both runs; a divergence confirms the finding.
