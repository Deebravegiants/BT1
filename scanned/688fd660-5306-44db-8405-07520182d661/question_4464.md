# Q4464: receive-underlying via deposit: mint shares whose backing was never received

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `recipient`, including a contract principal reach `receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) in a state where it mint shares whose backing was never received? Given that it pulls the underlying from a named account, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `recipient`, including a contract principal across its boundary values through `deposit` in simnet and assert `receive-underlying` never returns a value that breaks the invariant.
