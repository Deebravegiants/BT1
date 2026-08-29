# Q0776: uint-to-list-u64 via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `uint-to-list-u64` (mainnet/contracts/registry/v0-assets.clar:80) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it expands a bitmap into a 64-element list, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:80` -> `uint-to-list-u64`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `uint-to-list-u64` expands a bitmap into a 64-element list. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `uint-to-list-u64` returns is identical in both runs; a divergence confirms the finding.
