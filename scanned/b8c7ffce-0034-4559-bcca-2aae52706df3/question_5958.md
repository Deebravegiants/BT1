# Q5958: calc-principal-ratio-reduction via transfer: credit one side of an accounting pair without the other

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling the timing relative to a pledge or a liquidation, can an unprivileged attacker make `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) credit one side of an accounting pair without the other? `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `transfer` and credit one side of an accounting pair without the other.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the timing relative to a pledge or a liquidation across its boundary values through `transfer` in simnet and assert `calc-principal-ratio-reduction` never returns a value that breaks the invariant.
