# Q0120: mint can break PsmInfos / PsmDebt conservation

## Question
Can an unprivileged attacker call `mint` with crafted amounts, fees, or prices so `PsmInfos` and `PsmDebt` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/psm/src/lib.rs::mint
- Entrypoint: signed extrinsic `mint`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `PsmInfos`, `PsmDebt`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
