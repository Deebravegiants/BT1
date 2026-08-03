# Q0029: remove_liquidity can break Pools / LP issuance conservation

## Question
Can an unprivileged attacker call `remove_liquidity` with crafted amounts, fees, or prices so `Pools` and `LP issuance` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/asset-conversion/src/lib.rs::remove_liquidity
- Entrypoint: signed extrinsic `remove_liquidity`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `Pools`, `LP issuance`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
