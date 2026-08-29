# Q1668: convert-to-shares-preview via deposit: count one deposit as backing for two simultaneous claims

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls the vault's supply and asset state at the moment of the call reach `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) in a state where it count one deposit as backing for two simultaneous claims? Given that it returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: the vault's supply and asset state at the moment of the call
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `deposit` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the vault's supply and asset state at the moment of the call across its boundary values through `deposit` in simnet and assert `convert-to-shares-preview` never returns a value that breaks the invariant.
