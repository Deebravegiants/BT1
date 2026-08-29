# Q5878: resolve-price-feed via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling vault share price at the moment of the deposit leg, can an unprivileged attacker make `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) credit one side of an accounting pair without the other? `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with vault share price at the moment of the deposit leg, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
