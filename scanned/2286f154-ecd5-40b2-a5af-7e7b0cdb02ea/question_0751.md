# Q0751: remove_proxy can refund or slash deposits inconsistently

## Question
Can an unprivileged attacker drive `remove_proxy` through edge cases that reserve, refund, or slash auth-related deposits inconsistently with surviving authorization state?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::remove_proxy
- Entrypoint: public dispatch wrapper `remove_proxy`
- Attacker controls: nested call payloads, beneficiary, delegate, or target accounts, batched or wrapped execution context
- Exploit idea: Look for paths where deposit accounting and auth cleanup are not updated atomically.
- Invariant to test: Deposits backing public authorization state must decrease or refund exactly once when that state is consumed or removed.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Track reserved balances before and after creation, cancellation, consumption, and cleanup of the same auth object.
