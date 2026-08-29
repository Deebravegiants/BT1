# Q5850: receive-underlying via transfer: count one deposit as backing for two simultaneous claims

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) count one deposit as backing for two simultaneous claims? `receive-underlying` pulls the underlying from a named account, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `transfer` in simnet and assert `receive-underlying` never returns a value that breaks the invariant.
