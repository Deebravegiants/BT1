# Q5655: total-debt via liquidate-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
`total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) computes cumulative debt from `principal-scaled` and `index`. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the borrower targeted, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `liquidate-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `total-debt` touches, run `liquidate-redeem` with the borrower targeted, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
