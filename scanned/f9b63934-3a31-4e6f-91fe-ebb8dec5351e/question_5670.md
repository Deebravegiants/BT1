# Q5670: collateral-remove via repay: count one deposit as backing for two simultaneous claims

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling the `ft` trait principal, can an unprivileged attacker make `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) count one deposit as backing for two simultaneous claims? `collateral-remove` decrements the map and writes the entry before `send-tokens` executes, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `repay` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `repay` in simnet and assert `collateral-remove` never returns a value that breaks the invariant.
