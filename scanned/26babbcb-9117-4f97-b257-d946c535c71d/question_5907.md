# Q5907: get-liquidation-position via liquidate-redeem: mint shares whose backing was never received

## Question
`get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the seized zToken amount that is immediately redeemed, use that to mint shares whose backing was never received, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `get-liquidation-position` touches, run `liquidate-redeem` with the seized zToken amount that is immediately redeemed, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
