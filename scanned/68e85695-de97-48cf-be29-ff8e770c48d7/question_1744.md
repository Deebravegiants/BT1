# Q1744: set_claim_permission can expose underpriced public work

## Question
Can an unprivileged attacker abuse `set_claim_permission` with crafted call repetition, batching order, and surrounding state to force underpriced reads, writes, or iteration over `BondedPools` / `PoolMembers`, degrading block production in an in-scope way?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::set_claim_permission
- Entrypoint: signed extrinsic `set_claim_permission`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for public loops, repeated cleanup work, or input shapes whose real cost grows faster than charged weight.
- Invariant to test: Worst-case public cost must stay within charged weight and must not create a griefing route to persistent slowdown.
- Expected Immunefi impact: Permanent fund lock or block-production degradation from underpriced work
- Fast validation: Fuzz maximum list lengths, repeated tiny positions, and stale records; compare actual work to benchmark assumptions.
