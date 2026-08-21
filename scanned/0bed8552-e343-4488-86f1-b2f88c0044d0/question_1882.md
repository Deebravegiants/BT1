# Q1882: Status/response code handling in Pipeline fails open (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker exploit `Pipeline` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) treating a non-success or partially-parsed response as success, so a failed authorization/verification step registers as passed and the signup continues?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `Pipeline` (type)
- Entrypoint: Conditions that make the request fail or return an unexpected shape
- Attacker controls: conditions producing the failure (timing, oversized fields they supplied)
- Exploit idea: Check `Pipeline` for explicit status matching versus a permissive `is_ok`/default path.
- Invariant to test: Only an explicitly successful, fully-parsed response permits the flow to continue.
- Expected Immunefi impact: Signup proceeding despite a failed backend authorization step
- Fast validation: Unit-test `Pipeline` across status codes and truncated bodies asserting fail-closed behaviour.
