# Q3151: Status/response code handling in request fails open (backend/signup_post.rs)

## Question
Can an unprivileged attacker exploit `request` in [src/backend/signup_post.rs](src/backend/signup_post.rs) treating a non-success or partially-parsed response as success, so a failed authorization/verification step registers as passed and the signup continues?

## Target
- File/function: [src/backend/signup_post.rs](src/backend/signup_post.rs) -> `request` (function)
- Entrypoint: Conditions that make the request fail or return an unexpected shape
- Attacker controls: conditions producing the failure (timing, oversized fields they supplied)
- Exploit idea: Check `request` for explicit status matching versus a permissive `is_ok`/default path.
- Invariant to test: Only an explicitly successful, fully-parsed response permits the flow to continue.
- Expected Immunefi impact: Signup proceeding despite a failed backend authorization step
- Fast validation: Unit-test `request` across status codes and truncated bodies asserting fail-closed behaviour.
