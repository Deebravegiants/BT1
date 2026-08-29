# Q4457: resolve-pyth via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `min-collateral-expected`, drive `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) — which reads the Pyth storage record for a 32-byte ident — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `min-collateral-expected`, and assert the attacker's net token balance change is zero or negative.
