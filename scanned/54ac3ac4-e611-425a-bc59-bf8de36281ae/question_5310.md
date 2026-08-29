# Q5310: insert via repay: count one deposit as backing for two simultaneous claims

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling the `ft` trait principal, can an unprivileged attacker make `insert` (mainnet/contracts/market/v0-market-vault.clar:159) count one deposit as backing for two simultaneous claims? `insert` rewrites the whole registry entry for a user id, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `repay` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `repay` in simnet and assert `insert` never returns a value that breaks the invariant.
