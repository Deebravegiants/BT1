# Q0364: claim_rewards_to partial failure can leave ghost accounting

## Question
Can an unprivileged attacker force `claim_rewards_to` to fail after earlier state writes, leaving `RegisteredRelayers` or `RelayerRewards` partially updated and creating a theft or freeze condition?

## Target
- File/function: bridges/modules/relayers/src/lib.rs::claim_rewards_to
- Entrypoint: signed extrinsic `claim_rewards_to`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Target the latest possible failing branch after balances, deposits, or ownership state has already moved.
- Invariant to test: All touched storage must roll back atomically; no ghost holds, deposits, liabilities, or ownership edges may survive an error.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Use adversarial parameters plus nested batch execution and compare pre/post storage snapshots.
