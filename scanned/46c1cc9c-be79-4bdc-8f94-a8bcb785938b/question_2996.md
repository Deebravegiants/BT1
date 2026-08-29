# Q2996: find via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the future mask produced by the new debt bit reach `find` (mainnet/contracts/registry/v0-assets.clar:135) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it resolves an asset record from a principal through the `reverse` map, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the future mask produced by the new debt bit varied, and assert that the value `find` returns is identical in both runs; a divergence confirms the finding.
