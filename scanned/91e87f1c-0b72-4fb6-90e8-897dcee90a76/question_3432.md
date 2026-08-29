# Q3432: get-cached-indexes via accrue: make the per-user ledger and the vault aggregate disagree 

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls whether an earlier call in the same block already advanced last-update reach `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `accrue` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether an earlier call in the same block already advanced last-update across its boundary values through `accrue` in simnet and assert `get-cached-indexes` never returns a value that breaks the invariant.
