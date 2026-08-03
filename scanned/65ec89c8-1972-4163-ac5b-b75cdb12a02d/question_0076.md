# Q0076: register can break RegisteredRelayers / RelayerRewards conservation

## Question
Can an unprivileged attacker call `register` with crafted call repetition, batching order, and surrounding state so `RegisteredRelayers` and `RelayerRewards` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: bridges/modules/relayers/src/lib.rs::register
- Entrypoint: signed extrinsic `register`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `RegisteredRelayers`, `RelayerRewards`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
