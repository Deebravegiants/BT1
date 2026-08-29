# Q2010: calc-index-next via collateral-remove-redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `min-underlying`, can an unprivileged attacker make `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) have the same quantity scaled twice by two contracts that round differently? `calc-index-next` applies a multiplier to the current index, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `collateral-remove-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `min-underlying` across its boundary values through `collateral-remove-redeem` in simnet and assert `calc-index-next` never returns a value that breaks the invariant.
