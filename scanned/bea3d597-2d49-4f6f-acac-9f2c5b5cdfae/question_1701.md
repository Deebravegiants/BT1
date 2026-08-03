# Q1701: create_swap can expose underpriced public work

## Question
Can an unprivileged attacker abuse `create_swap` with crafted beneficiary, delegate, or target accounts to force underpriced reads, writes, or iteration over `PendingSwaps` / `hashlock state`, degrading block production in an in-scope way?

## Target
- File/function: substrate/frame/atomic-swap/src/lib.rs::create_swap
- Entrypoint: signed extrinsic `create_swap`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Look for public loops, repeated cleanup work, or input shapes whose real cost grows faster than charged weight.
- Invariant to test: Worst-case public cost must stay within charged weight and must not create a griefing route to persistent slowdown.
- Expected Immunefi impact: Permanent fund lock or block-production degradation from underpriced work
- Fast validation: Fuzz maximum list lengths, repeated tiny positions, and stale records; compare actual work to benchmark assumptions.
