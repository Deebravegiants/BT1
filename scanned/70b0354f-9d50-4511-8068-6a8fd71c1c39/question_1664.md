# Q1664: unpack-u16 via repay: count one deposit as backing for two simultaneous claims

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `amount`, including far above the real debt (the capping path) reach `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) in a state where it count one deposit as backing for two simultaneous claims? Given that it unpacks eight u16 curve fields from one packed word, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `repay` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `amount`, including far above the real debt (the capping path) varied, and assert that the value `unpack-u16` returns is identical in both runs; a divergence confirms the finding.
