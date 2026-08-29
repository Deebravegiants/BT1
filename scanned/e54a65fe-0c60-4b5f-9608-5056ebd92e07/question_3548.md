# Q3548: resolve-pyth via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the future mask produced by the new debt bit reach `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reads the Pyth storage record for a 32-byte ident, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the future mask produced by the new debt bit varied, and assert that the value `resolve-pyth` returns is identical in both runs; a divergence confirms the finding.
