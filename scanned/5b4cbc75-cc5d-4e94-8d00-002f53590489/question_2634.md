# Q2634: receive-tokens via liquidate-redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the borrower targeted, can an unprivileged attacker make `receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) have the same quantity scaled twice by two contracts that round differently? `receive-tokens` pulls an asset from a named account, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `liquidate-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the borrower targeted across its boundary values through `liquidate-redeem` in simnet and assert `receive-tokens` never returns a value that breaks the invariant.
