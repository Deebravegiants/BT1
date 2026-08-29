# Q2538: calc-cumulative-debt via deposit: have the same quantity scaled twice by two contracts that 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling whether the vault is at a zero-supply or zero-asset edge, can an unprivileged attacker make `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) have the same quantity scaled twice by two contracts that round differently? `calc-cumulative-debt` multiplies scaled principal by an index, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `deposit` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz whether the vault is at a zero-supply or zero-asset edge across its boundary values through `deposit` in simnet and assert `calc-cumulative-debt` never returns a value that breaks the invariant.
