# Q2136: unpack-u16 via deposit: credit one side of an accounting pair without the other

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `recipient`, including a contract principal reach `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) in a state where it credit one side of an accounting pair without the other? Given that it unpacks eight u16 curve fields from one packed word, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `recipient`, including a contract principal across its boundary values through `deposit` in simnet and assert `unpack-u16` never returns a value that breaks the invariant.
