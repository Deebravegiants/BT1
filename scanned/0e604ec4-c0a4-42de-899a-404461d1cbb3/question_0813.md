# Q0813: get-liquidation-position via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling the `ft` trait principal deciding which vault is routed to, drive `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) — which returns enabled collateral plus ALL debt, a different view from the one borrow validated against — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `get-liquidation-position` touches, run `supply-collateral-add` with the `ft` trait principal deciding which vault is routed to, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
