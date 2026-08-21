# Q2170: Time source trusted by InternalOnly (logger.rs)

## Question
Can an unprivileged attacker exploit `InternalOnly` in [src/logger.rs](src/logger.rs) trusting wall-clock time for freshness/expiry (token validity, capture timestamps), where clock movement through normal operation makes stale material appear fresh or lets timestamps be non-monotonic?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `InternalOnly` (type)
- Entrypoint: Signup timed around clock adjustment/boot conditions
- Attacker controls: the timing of their session relative to clock changes
- Exploit idea: Check whether `InternalOnly` uses a monotonic source for elapsed-time decisions.
- Invariant to test: Freshness decisions use a monotonic clock; wall-clock values are data, never authority.
- Expected Immunefi impact: Expired credential or stale capture accepted as fresh
- Fast validation: Unit-test `InternalOnly` with non-monotonic clock sequences asserting correct expiry.
