# Q3126: price-multi-resolve via liquidate-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the seized zToken amount that is immediately redeemed, can an unprivileged attacker make `price-multi-resolve` (mainnet/contracts/market/v0-4-market.clar:397) leave a residue that no reconciliation pass ever inspects? `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:397` -> `price-multi-resolve`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Reach it through `liquidate-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the seized zToken amount that is immediately redeemed across its boundary values through `liquidate-redeem` in simnet and assert `price-multi-resolve` never returns a value that breaks the invariant.
