# Q0754: control_inherited_account can refund or slash deposits inconsistently

## Question
Can an unprivileged attacker drive `control_inherited_account` through edge cases that reserve, refund, or slash auth-related deposits inconsistently with surviving authorization state?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::control_inherited_account
- Entrypoint: signed extrinsic `control_inherited_account`
- Attacker controls: nested call payloads
- Exploit idea: Look for paths where deposit accounting and auth cleanup are not updated atomically.
- Invariant to test: Deposits backing public authorization state must decrease or refund exactly once when that state is consumed or removed.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Track reserved balances before and after creation, cancellation, consumption, and cleanup of the same auth object.
