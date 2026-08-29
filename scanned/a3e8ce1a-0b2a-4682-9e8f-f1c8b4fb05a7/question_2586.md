# Q2586: next-liquidity-index via deposit: have the same quantity scaled twice by two contracts that 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `recipient`, including a contract principal, can an unprivileged attacker make `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) have the same quantity scaled twice by two contracts that round differently? `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `deposit` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `recipient`, including a contract principal across its boundary values through `deposit` in simnet and assert `next-liquidity-index` never returns a value that breaks the invariant.
