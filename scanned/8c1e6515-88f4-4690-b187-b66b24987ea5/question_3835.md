# Q3835: withdraw_unbonded can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `withdraw_unbonded` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::withdraw_unbonded
- Entrypoint: signed extrinsic `withdraw_unbonded`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: Permanent fund lock or block-production degradation from underpriced work
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
