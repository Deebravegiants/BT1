# Q5394: get-bitmap via borrow: count one deposit as backing for two simultaneous claims

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the future mask produced by the new debt bit, can an unprivileged attacker make `get-bitmap` (mainnet/contracts/registry/v0-assets.clar:145) count one deposit as backing for two simultaneous claims? `get-bitmap` returns the global enabled bitmap that every position read filters on, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:145` -> `get-bitmap`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `get-bitmap` returns the global enabled bitmap that every position read filters on. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the future mask produced by the new debt bit across its boundary values through `borrow` in simnet and assert `get-bitmap` never returns a value that breaks the invariant.
