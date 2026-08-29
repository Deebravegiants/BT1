# Q2226: is-liquidation-paused via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `debt-amount`, can an unprivileged attacker make `is-liquidation-paused` (mainnet/contracts/market/v0-4-market.clar:691) have the same quantity scaled twice by two contracts that round differently? `is-liquidation-paused` returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:691` -> `is-liquidation-paused`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `is-liquidation-paused` returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `debt-amount` across its boundary values through `liquidate` in simnet and assert `is-liquidation-paused` never returns a value that breaks the invariant.
