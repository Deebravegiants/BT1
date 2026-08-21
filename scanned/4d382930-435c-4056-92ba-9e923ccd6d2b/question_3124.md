# Q3124: Time source trusted by to_uuid (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker exploit `to_uuid` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) trusting wall-clock time for freshness/expiry (token validity, capture timestamps), where clock movement through normal operation makes stale material appear fresh or lets timestamps be non-monotonic?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `to_uuid` (function)
- Entrypoint: Signup timed around clock adjustment/boot conditions
- Attacker controls: the timing of their session relative to clock changes
- Exploit idea: Check whether `to_uuid` uses a monotonic source for elapsed-time decisions.
- Invariant to test: Freshness decisions use a monotonic clock; wall-clock values are data, never authority.
- Expected Immunefi impact: Expired credential or stale capture accepted as fresh
- Fast validation: Unit-test `to_uuid` with non-monotonic clock sequences asserting correct expiry.
