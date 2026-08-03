# Q0726: remove_expired_approval can refund or slash deposits inconsistently

## Question
Can an unprivileged attacker drive `remove_expired_approval` through edge cases that reserve, refund, or slash auth-related deposits inconsistently with surviving authorization state?

## Target
- File/function: substrate/frame/identity/src/lib.rs::remove_expired_approval
- Entrypoint: signed extrinsic `remove_expired_approval`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for paths where deposit accounting and auth cleanup are not updated atomically.
- Invariant to test: Deposits backing public authorization state must decrease or refund exactly once when that state is consumed or removed.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Track reserved balances before and after creation, cancellation, consumption, and cleanup of the same auth object.
