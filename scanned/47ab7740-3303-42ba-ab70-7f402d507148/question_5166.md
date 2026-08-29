# Q5166: get-position via borrow: count one deposit as backing for two simultaneous claims

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the future mask produced by the new debt bit, can an unprivileged attacker make `get-position` (mainnet/contracts/market/v0-4-market.clar:466) count one deposit as backing for two simultaneous claims? `get-position` returns only rows whose bit is set in the ENABLED bitmap, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the future mask produced by the new debt bit across its boundary values through `borrow` in simnet and assert `get-position` never returns a value that breaks the invariant.
