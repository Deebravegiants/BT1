# Q2242: calc-liq-factor-bound via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the trait principals supplied per entry, can an unprivileged attacker make `calc-liq-factor-bound` (mainnet/contracts/market/v0-4-market.clar:718) have the same quantity scaled twice by two contracts that round differently? `calc-liq-factor-bound` scales the penalty between a min and a max, capped at the max, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:718` -> `calc-liq-factor-bound`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `calc-liq-factor-bound` scales the penalty between a min and a max, capped at the max. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate-multi` with the trait principals supplied per entry, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
