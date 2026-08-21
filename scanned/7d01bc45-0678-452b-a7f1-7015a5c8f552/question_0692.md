# Q0692: Time source trusted by make_face_tar (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker exploit `make_face_tar` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) trusting wall-clock time for freshness/expiry (token validity, capture timestamps), where clock movement through normal operation makes stale material appear fresh or lets timestamps be non-monotonic?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_face_tar` (function)
- Entrypoint: Signup timed around clock adjustment/boot conditions
- Attacker controls: the timing of their session relative to clock changes
- Exploit idea: Check whether `make_face_tar` uses a monotonic source for elapsed-time decisions.
- Invariant to test: Freshness decisions use a monotonic clock; wall-clock values are data, never authority.
- Expected Immunefi impact: Expired credential or stale capture accepted as fresh
- Fast validation: Unit-test `make_face_tar` with non-monotonic clock sequences asserting correct expiry.
