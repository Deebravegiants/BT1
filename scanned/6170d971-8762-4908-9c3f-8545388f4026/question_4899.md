# Q4899: resolve-price-feed via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
`resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing vault share price at the moment of the deposit leg, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-price-feed` touches, run `supply-collateral-add` with vault share price at the moment of the deposit leg, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
