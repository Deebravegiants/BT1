# Q4467: ubalance via accrue: credit one side of an accounting pair without the other

## Question
`ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing the block time at which accrual is first triggered in a block, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `ubalance` touches, run `accrue` with the block time at which accrual is first triggered in a block, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
