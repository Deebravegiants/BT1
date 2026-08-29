# Q3764: refresh via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls which borrowers are placed early versus late in the batch reach `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with which borrowers are placed early versus late in the batch varied, and assert that the value `refresh` returns is identical in both runs; a divergence confirms the finding.
