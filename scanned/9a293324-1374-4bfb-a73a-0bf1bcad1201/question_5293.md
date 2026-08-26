# Q5293: securitycontext accessor in validateLocalDescendingPath

## Question
Can an unprivileged attacker reaching `pkg/apis/core/validation/validation.go` via create/update request body validated by the kube-apiserver registry, supplying a Pod whose container securityContext overrides pod-level fields, cause `validateLocalDescendingPath` to be exercised such that the accessor merges pod/container security fields so a restricted value is silently dropped, breaking the invariant that every user-submitted field is fully validated before persistence; no malformed/protected value is stored, and leading to Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption?

## Target
- File/function: `pkg/apis/core/validation/validation.go` -> `validateLocalDescendingPath`
- Entrypoint: create/update request body validated by the kube-apiserver registry
- Attacker controls: a Pod whose container securityContext overrides pod-level fields
- Exploit idea: the accessor merges pod/container security fields so a restricted value is silently dropped
- Invariant to test: every user-submitted field is fully validated before persistence; no malformed/protected value is stored
- Expected Immunefi impact: Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption
- Fast validation: validation table test: pass the crafted object, assert a field.Error is returned
