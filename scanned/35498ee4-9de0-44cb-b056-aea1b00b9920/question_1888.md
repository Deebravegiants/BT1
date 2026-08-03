# Q1888: buy_ticket can expose underpriced public governance work

## Question
Can an unprivileged attacker abuse `buy_ticket` to create underpriced scans, cleanups, or list processing over `Lottery` / `Tickets`, degrading block production or permanently bloating state?

## Target
- File/function: substrate/frame/lottery/src/lib.rs::buy_ticket
- Entrypoint: signed extrinsic `buy_ticket`
- Attacker controls: nested call payloads
- Exploit idea: Look for public loops over votes, proposals, referenda, tips, or bounties whose real cost grows faster than charged weight.
- Invariant to test: Worst-case public governance maintenance must stay within charged weight and storage limits.
- Expected Immunefi impact: Permanent lock of funds or governance queue corruption
- Fast validation: Fuzz maximum list sizes, duplicate-heavy inputs, and stale-record cleanup loops.
