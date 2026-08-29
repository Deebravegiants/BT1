# Q0296: unpack-u16 via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `amount` used for BOTH the collateral removal and the share redemption reach `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it unpacks eight u16 curve fields from one packed word, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `amount` used for BOTH the collateral removal and the share redemption varied, and assert that the value `unpack-u16` returns is identical in both runs; a divergence confirms the finding.
