# Q0074: claim_rewards_to can break RegisteredRelayers / RelayerRewards conservation

## Question
Can an unprivileged attacker call `claim_rewards_to` with crafted beneficiary, delegate, or target accounts so `RegisteredRelayers` and `RelayerRewards` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: bridges/modules/relayers/src/lib.rs::claim_rewards_to
- Entrypoint: signed extrinsic `claim_rewards_to`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `RegisteredRelayers`, `RelayerRewards`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
