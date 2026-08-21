# Q3093: Time source trusted by initialize_signup (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `initialize_signup` in [src/agents/image_notary.rs](src/agents/image_notary.rs) trusting wall-clock time for freshness/expiry (token validity, capture timestamps), where clock movement through normal operation makes stale material appear fresh or lets timestamps be non-monotonic?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `initialize_signup` (function)
- Entrypoint: Signup timed around clock adjustment/boot conditions
- Attacker controls: the timing of their session relative to clock changes
- Exploit idea: Check whether `initialize_signup` uses a monotonic source for elapsed-time decisions.
- Invariant to test: Freshness decisions use a monotonic clock; wall-clock values are data, never authority.
- Expected Immunefi impact: Expired credential or stale capture accepted as fresh
- Fast validation: Unit-test `initialize_signup` with non-monotonic clock sequences asserting correct expiry.
