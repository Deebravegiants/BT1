# Q1955: Time source trusted by new (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker exploit `new` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) trusting wall-clock time for freshness/expiry (token validity, capture timestamps), where clock movement through normal operation makes stale material appear fresh or lets timestamps be non-monotonic?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `new` (function)
- Entrypoint: Signup timed around clock adjustment/boot conditions
- Attacker controls: the timing of their session relative to clock changes
- Exploit idea: Check whether `new` uses a monotonic source for elapsed-time decisions.
- Invariant to test: Freshness decisions use a monotonic clock; wall-clock values are data, never authority.
- Expected Immunefi impact: Expired credential or stale capture accepted as fresh
- Fast validation: Unit-test `new` with non-monotonic clock sequences asserting correct expiry.
