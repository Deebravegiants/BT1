# Q1880: propose can expose underpriced public governance work

## Question
Can an unprivileged attacker abuse `propose` to create underpriced scans, cleanups, or list processing over `PublicProps` / `DepositOf`, degrading block production or permanently bloating state?

## Target
- File/function: substrate/frame/democracy/src/lib.rs::propose
- Entrypoint: signed extrinsic `propose`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Look for public loops over votes, proposals, referenda, tips, or bounties whose real cost grows faster than charged weight.
- Invariant to test: Worst-case public governance maintenance must stay within charged weight and storage limits.
- Expected Immunefi impact: Permanent lock of funds or governance queue corruption
- Fast validation: Fuzz maximum list sizes, duplicate-heavy inputs, and stale-record cleanup loops.
