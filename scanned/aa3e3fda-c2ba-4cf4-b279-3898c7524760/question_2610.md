# Q2610: is-healthy-with-mask via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `is-healthy-with-mask` (mainnet/contracts/market/v0-4-market.clar:663) have the same quantity scaled twice by two contracts that round differently? `is-healthy-with-mask` resolves an egroup for a caller-influenced mask and applies its LTV-BORROW, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:663` -> `is-healthy-with-mask`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `is-healthy-with-mask` resolves an egroup for a caller-influenced mask and applies its LTV-BORROW. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `receiver`, including a contract principal across its boundary values through `collateral-remove` in simnet and assert `is-healthy-with-mask` never returns a value that breaks the invariant.
