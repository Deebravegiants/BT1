# Q0621: ubalance via transfer: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the timing relative to a pledge or a liquidation, drive `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) — which reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `transfer` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `ubalance` touches, run `transfer` with the timing relative to a pledge or a liquidation, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
