# Q5571: receive-tokens via liquidate-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
`receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) pulls an asset from a named account. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the borrower targeted, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `liquidate-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `receive-tokens` touches, run `liquidate-redeem` with the borrower targeted, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
