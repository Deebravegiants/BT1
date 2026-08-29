# Q5390: get-cached-indexes via accrue: count one deposit as backing for two simultaneous claims

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the block time at which accrual is first triggered in a block, can an unprivileged attacker make `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) count one deposit as backing for two simultaneous claims? `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the block time at which accrual is first triggered in a block varied, and assert that the value `get-cached-indexes` returns is identical in both runs; a divergence confirms the finding.
