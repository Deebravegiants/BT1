# Q0597: zip via deposit: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling `min-out`, drive `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) — which pairs the utilization and rate point lists element by element — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `zip` touches, run `deposit` with `min-out`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
