# Q2250: calc-liquidation-params via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the trait principals supplied per entry, can an unprivileged attacker make `calc-liquidation-params` (mainnet/contracts/market/v0-4-market.clar:739) have the same quantity scaled twice by two contracts that round differently? `calc-liquidation-params` chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:739` -> `calc-liquidation-params`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `calc-liquidation-params` chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the trait principals supplied per entry across its boundary values through `liquidate-multi` in simnet and assert `calc-liquidation-params` never returns a value that breaks the invariant.
