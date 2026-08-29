# Q5247: receive-tokens via transfer: make the per-user ledger and the vault aggregate disagree 

## Question
`receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) pulls an asset from a named account. Can an unprivileged caller of `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), by choosing `amount`, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `transfer` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `receive-tokens` touches, run `transfer` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
