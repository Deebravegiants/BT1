# Q1874: remove_other_vote can expose underpriced public governance work

## Question
Can an unprivileged attacker abuse `remove_other_vote` to create underpriced scans, cleanups, or list processing over `VotingFor` / `class locks`, degrading block production or permanently bloating state?

## Target
- File/function: substrate/frame/conviction-voting/src/lib.rs::remove_other_vote
- Entrypoint: signed extrinsic `remove_other_vote`
- Attacker controls: IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts
- Exploit idea: Look for public loops over votes, proposals, referenda, tips, or bounties whose real cost grows faster than charged weight.
- Invariant to test: Worst-case public governance maintenance must stay within charged weight and storage limits.
- Expected Immunefi impact: Permanent lock of funds or governance queue corruption
- Fast validation: Fuzz maximum list sizes, duplicate-heavy inputs, and stale-record cleanup loops.
