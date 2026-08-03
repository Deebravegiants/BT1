# Q0752: approve_attempt can refund or slash deposits inconsistently

## Question
Can an unprivileged attacker drive `approve_attempt` through edge cases that reserve, refund, or slash auth-related deposits inconsistently with surviving authorization state?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::approve_attempt
- Entrypoint: signed extrinsic `approve_attempt`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for paths where deposit accounting and auth cleanup are not updated atomically.
- Invariant to test: Deposits backing public authorization state must decrease or refund exactly once when that state is consumed or removed.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Track reserved balances before and after creation, cancellation, consumption, and cleanup of the same auth object.
