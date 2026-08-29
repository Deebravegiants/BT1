# Q2178: collateral-remove via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the trait principals supplied per entry, can an unprivileged attacker make `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) have the same quantity scaled twice by two contracts that round differently? `collateral-remove` decrements the map and writes the entry before `send-tokens` executes, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the trait principals supplied per entry across its boundary values through `liquidate-multi` in simnet and assert `collateral-remove` never returns a value that breaks the invariant.
