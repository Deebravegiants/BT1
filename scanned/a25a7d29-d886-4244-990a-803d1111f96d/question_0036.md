# Q0036: unstake can break Pools / PoolStakers conservation

## Question
Can an unprivileged attacker call `unstake` with crafted amounts, fees, or prices, IDs, hashes, nonces, or location fields so `Pools` and `PoolStakers` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/asset-rewards/src/lib.rs::unstake
- Entrypoint: signed extrinsic `unstake`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `Pools`, `PoolStakers`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
