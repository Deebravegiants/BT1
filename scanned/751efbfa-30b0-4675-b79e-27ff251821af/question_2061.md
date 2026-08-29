# Q2061: calc-utilization via call-ststx-ratio: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), controlling the block and transaction position at which the external ratio is fetched, drive `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) — which divides debt by available liquidity, which can exceed BPS when debt outruns assets — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `call-ststx-ratio` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `calc-utilization` touches, run `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
