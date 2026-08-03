# Q0070: transfer_allow_death can break Account / TotalIssuance conservation

## Question
Can an unprivileged attacker call `transfer_allow_death` with crafted amounts, fees, or prices, beneficiary, delegate, or target accounts so `Account` and `TotalIssuance` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/balances/src/lib.rs::transfer_allow_death
- Entrypoint: signed extrinsic `transfer_allow_death`
- Attacker controls: amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `Account`, `TotalIssuance`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
