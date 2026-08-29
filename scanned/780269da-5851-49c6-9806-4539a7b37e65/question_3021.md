# Q3021: calc-principal-ratio-reduction via transfer: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the timing relative to a pledge or a liquidation, drive `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) — which reduces scaled principal proportionally to an amount over total debt — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `transfer` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `calc-principal-ratio-reduction` touches, run `transfer` with the timing relative to a pledge or a liquidation, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
