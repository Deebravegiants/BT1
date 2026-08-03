# Q0087: purchase_credit can break Regions / Workplan conservation

## Question
Can an unprivileged attacker call `purchase_credit` with crafted amounts, fees, or prices, beneficiary, delegate, or target accounts so `Regions` and `Workplan` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/broker/src/lib.rs::purchase_credit
- Entrypoint: signed extrinsic `purchase_credit`
- Attacker controls: amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `Regions`, `Workplan`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
