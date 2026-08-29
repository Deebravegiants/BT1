# Q1028: refresh via repay: count one deposit as backing for two simultaneous claims

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `amount`, including far above the real debt (the capping path) reach `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) in a state where it count one deposit as backing for two simultaneous claims? Given that it rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `repay` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `amount`, including far above the real debt (the capping path) varied, and assert that the value `refresh` returns is identical in both runs; a divergence confirms the finding.
