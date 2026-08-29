# Q0678: unpack-u16 via redeem: mint shares whose backing was never received

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `recipient`, can an unprivileged attacker make `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) mint shares whose backing was never received? `unpack-u16` unpacks eight u16 curve fields from one packed word, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `recipient` across its boundary values through `redeem` in simnet and assert `unpack-u16` never returns a value that breaks the invariant.
