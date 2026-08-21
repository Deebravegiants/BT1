# Q2017: Status/response code handling in request_package fails open (backend/presigned_url.rs)

## Question
Can an unprivileged attacker exploit `request_package` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) treating a non-success or partially-parsed response as success, so a failed authorization/verification step registers as passed and the signup continues?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `request_package` (function)
- Entrypoint: Conditions that make the request fail or return an unexpected shape
- Attacker controls: conditions producing the failure (timing, oversized fields they supplied)
- Exploit idea: Check `request_package` for explicit status matching versus a permissive `is_ok`/default path.
- Invariant to test: Only an explicitly successful, fully-parsed response permits the flow to continue.
- Expected Immunefi impact: Signup proceeding despite a failed backend authorization step
- Fast validation: Unit-test `request_package` across status codes and truncated bodies asserting fail-closed behaviour.
