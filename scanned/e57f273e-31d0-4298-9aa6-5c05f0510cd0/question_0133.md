# Q0133: set_controller can break Ledger / Nominators conservation

## Question
Can an unprivileged attacker call `set_controller` with crafted call repetition, batching order, and surrounding state so `Ledger` and `Nominators` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/staking/src/pallet/mod.rs::set_controller
- Entrypoint: signed extrinsic `set_controller`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `Ledger`, `Nominators`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
