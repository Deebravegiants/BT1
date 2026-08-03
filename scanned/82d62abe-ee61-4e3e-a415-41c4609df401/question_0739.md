# Q0739: ensure_updated can refund or slash deposits inconsistently

## Question
Can an unprivileged attacker drive `ensure_updated` through edge cases that reserve, refund, or slash auth-related deposits inconsistently with surviving authorization state?

## Target
- File/function: substrate/frame/preimage/src/lib.rs::ensure_updated
- Entrypoint: signed extrinsic `ensure_updated`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Look for paths where deposit accounting and auth cleanup are not updated atomically.
- Invariant to test: Deposits backing public authorization state must decrease or refund exactly once when that state is consumed or removed.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Track reserved balances before and after creation, cancellation, consumption, and cleanup of the same auth object.
