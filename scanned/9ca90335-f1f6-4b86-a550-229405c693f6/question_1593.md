# Q1593: linear-interpolate via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling vault share price at the moment of the deposit leg, drive `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) — which interpolates between two points, dividing by `(- x2 x1)` — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `linear-interpolate` touches, run `supply-collateral-add` with vault share price at the moment of the deposit leg, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
