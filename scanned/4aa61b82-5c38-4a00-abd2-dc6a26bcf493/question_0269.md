# Q0269: resolve-pyth via call-ststx-ratio: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), controlling the block and transaction position at which the external ratio is fetched, drive `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) — which reads the Pyth storage record for a 32-byte ident — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `call-ststx-ratio` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `call-ststx-ratio` call, then the attacker-shaped one with the block and transaction position at which the external ratio is fetched, and assert the attacker's net token balance change is zero or negative.
