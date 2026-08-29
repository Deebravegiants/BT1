# Q4634: get-cached-indexes via deposit: destroy value through a truncation the opposite operation 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `recipient`, including a contract principal, can an unprivileged attacker make `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) destroy value through a truncation the opposite operation does not restore? `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `recipient`, including a contract principal varied, and assert that the value `get-cached-indexes` returns is identical in both runs; a divergence confirms the finding.
