# Q3753: add_liquidity can accumulate hard-to-clean attacker state

## Question
Can an unprivileged attacker use `add_liquidity` repeatedly to create attacker-owned state that is valid but disproportionately expensive for honest users or future public maintenance paths to clean up?

## Target
- File/function: substrate/frame/asset-conversion/src/lib.rs::add_liquidity
- Entrypoint: signed extrinsic `add_liquidity`
- Attacker controls: amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Search for objects whose creation is cheap, whose cleanup is public, and whose worst-case cleanup shape is more expensive than creation.
- Invariant to test: Attacker-created public state must not create a durable griefing asymmetry against honest users or maintenance flows.
- Expected Immunefi impact: Permanent fund lock or block-production degradation from underpriced work
- Fast validation: Mass-create the smallest legal objects, then measure the cost and ergonomics of public cleanup and follow-on honest use.
