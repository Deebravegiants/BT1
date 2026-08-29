# Q5715: resolve-dia via collateral-remove-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
`resolve-dia` (mainnet/contracts/market/v0-4-market.clar:326) derives a (string-ascii 32) key from a (buff 32) ident. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing remaining zToken collateral whose price moves with the redeem, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:326` -> `resolve-dia`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `resolve-dia` derives a (string-ascii 32) key from a (buff 32) ident. Reach it through `collateral-remove-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-dia` touches, run `collateral-remove-redeem` with remaining zToken collateral whose price moves with the redeem, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
