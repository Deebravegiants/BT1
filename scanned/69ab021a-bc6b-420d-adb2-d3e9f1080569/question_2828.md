# Q2828: scale-debt-for-liquidation via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the redemption receiver reach `scale-debt-for-liquidation` (mainnet/contracts/market/v0-4-market.clar:858) in a state where it credit one side of an accounting pair without the other? Given that it re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:858` -> `scale-debt-for-liquidation`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `scale-debt-for-liquidation` re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the redemption receiver varied, and assert that the value `scale-debt-for-liquidation` returns is identical in both runs; a divergence confirms the finding.
