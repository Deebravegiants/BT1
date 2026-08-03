# Q0124: bond can break Ledger / Nominators conservation

## Question
Can an unprivileged attacker call `bond` with crafted amounts, fees, or prices so `Ledger` and `Nominators` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/staking/src/pallet/mod.rs::bond
- Entrypoint: signed extrinsic `bond`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `Ledger`, `Nominators`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
