# Q5466: calc-index-next via accrue: count one deposit as backing for two simultaneous claims

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the utilization the rate is interpolated at, can an unprivileged attacker make `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) count one deposit as backing for two simultaneous claims? `calc-index-next` applies a multiplier to the current index, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the utilization the rate is interpolated at across its boundary values through `accrue` in simnet and assert `calc-index-next` never returns a value that breaks the invariant.
