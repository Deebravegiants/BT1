# Q0993: vault-system-borrow via repay: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling `on-behalf-of`, naming any third-party principal, drive `vault-system-borrow` (mainnet/contracts/market/v0-4-market.clar:198) — which routes a borrow to one of six vaults by asset id — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:198` -> `vault-system-borrow`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `vault-system-borrow` routes a borrow to one of six vaults by asset id. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `vault-system-borrow` touches, run `repay` with `on-behalf-of`, naming any third-party principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
