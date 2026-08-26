# Q5739: negative/zero value in validateResourceRequirements

## Question
Can an unprivileged attacker reaching `pkg/apis/core/validation/validation.go` via create/update request body validated by the kube-apiserver registry, supplying a numeric spec field set negative, zero, or MaxInt, cause `validateResourceRequirements` to be exercised such that validation misses a range check, persisting a value that corrupts accounting or scheduling, breaking the invariant that every user-submitted field is fully validated before persistence; no malformed/protected value is stored, and leading to Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption?

## Target
- File/function: `pkg/apis/core/validation/validation.go` -> `validateResourceRequirements`
- Entrypoint: create/update request body validated by the kube-apiserver registry
- Attacker controls: a numeric spec field set negative, zero, or MaxInt
- Exploit idea: validation misses a range check, persisting a value that corrupts accounting or scheduling
- Invariant to test: every user-submitted field is fully validated before persistence; no malformed/protected value is stored
- Expected Immunefi impact: Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption
- Fast validation: validation table test: pass the crafted object, assert a field.Error is returned
