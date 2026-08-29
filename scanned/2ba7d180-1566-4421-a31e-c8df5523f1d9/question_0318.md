# Q0318: merge-price via collateral-add: mint shares whose backing was never received

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling call ordering within the block, can an unprivileged attacker make `merge-price` (mainnet/contracts/market/v0-4-market.clar:506) mint shares whose backing was never received? `merge-price` attaches a price to an asset record by position in the fold, not by asset id, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:506` -> `merge-price`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `merge-price` attaches a price to an asset record by position in the fold, not by asset id. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz call ordering within the block across its boundary values through `collateral-add` in simnet and assert `merge-price` never returns a value that breaks the invariant.
