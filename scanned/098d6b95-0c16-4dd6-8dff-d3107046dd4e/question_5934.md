# Q5934: next-index via redeem: credit one side of an accounting pair without the other

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the gap between the `assets` var and the real balance, can an unprivileged attacker make `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) credit one side of an accounting pair without the other? `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the gap between the `assets` var and the real balance across its boundary values through `redeem` in simnet and assert `next-index` never returns a value that breaks the invariant.
