# Q2720: calc-index-next via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the redemption receiver reach `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) in a state where it credit one side of an accounting pair without the other? Given that it applies a multiplier to the current index, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the redemption receiver varied, and assert that the value `calc-index-next` returns is identical in both runs; a divergence confirms the finding.
