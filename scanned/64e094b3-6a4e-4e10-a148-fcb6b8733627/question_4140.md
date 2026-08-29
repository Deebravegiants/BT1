# Q4140: relevant via collateral-add: mint shares whose backing was never received

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the position's existing collateral and debt composition reach `relevant` (mainnet/contracts/market/v0-market-vault.clar:175) in a state where it mint shares whose backing was never received? Given that it drops any position row whose bit is not present in the enabled mask, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the position's existing collateral and debt composition across its boundary values through `collateral-add` in simnet and assert `relevant` never returns a value that breaks the invariant.
