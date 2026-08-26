# Q5617: name injection in validatePodSpecSecurityContext

## Question
Can an unprivileged attacker reaching `pkg/apis/core/validation/validation.go` via create/update request body validated by the kube-apiserver registry, supplying an object name/namespace with `/`, `..`, or unicode confusables, cause `validatePodSpecSecurityContext` to be exercised such that name validation accepts a value that later resolves to a different key or path, breaking the invariant that every user-submitted field is fully validated before persistence; no malformed/protected value is stored, and leading to Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption?

## Target
- File/function: `pkg/apis/core/validation/validation.go` -> `validatePodSpecSecurityContext`
- Entrypoint: create/update request body validated by the kube-apiserver registry
- Attacker controls: an object name/namespace with `/`, `..`, or unicode confusables
- Exploit idea: name validation accepts a value that later resolves to a different key or path
- Invariant to test: every user-submitted field is fully validated before persistence; no malformed/protected value is stored
- Expected Immunefi impact: Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption
- Fast validation: validation table test: pass the crafted object, assert a field.Error is returned
