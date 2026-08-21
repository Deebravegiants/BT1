# Q1974: Status/response code handling in MANAGEMENT_BACKEND_URL fails open (backend/endpoints.rs)

## Question
Can an unprivileged attacker exploit `MANAGEMENT_BACKEND_URL` in [src/backend/endpoints.rs](src/backend/endpoints.rs) treating a non-success or partially-parsed response as success, so a failed authorization/verification step registers as passed and the signup continues?

## Target
- File/function: [src/backend/endpoints.rs](src/backend/endpoints.rs) -> `MANAGEMENT_BACKEND_URL` (item)
- Entrypoint: Conditions that make the request fail or return an unexpected shape
- Attacker controls: conditions producing the failure (timing, oversized fields they supplied)
- Exploit idea: Check `MANAGEMENT_BACKEND_URL` for explicit status matching versus a permissive `is_ok`/default path.
- Invariant to test: Only an explicitly successful, fully-parsed response permits the flow to continue.
- Expected Immunefi impact: Signup proceeding despite a failed backend authorization step
- Fast validation: Unit-test `MANAGEMENT_BACKEND_URL` across status codes and truncated bodies asserting fail-closed behaviour.
