# Q2658: immutable field in ValidateObjectMetaUpdate

## Question
Can an unprivileged attacker reaching `pkg/apis/core/validation/validation.go` via create/update request body validated by the kube-apiserver registry, supplying an update mutating a field validation should freeze, cause `ValidateObjectMetaUpdate` to be exercised such that update validation omits the immutability check, allowing mutation of a security-relevant field, breaking the invariant that every user-submitted field is fully validated before persistence; no malformed/protected value is stored, and leading to Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption?

## Target
- File/function: `pkg/apis/core/validation/validation.go` -> `ValidateObjectMetaUpdate`
- Entrypoint: create/update request body validated by the kube-apiserver registry
- Attacker controls: an update mutating a field validation should freeze
- Exploit idea: update validation omits the immutability check, allowing mutation of a security-relevant field
- Invariant to test: every user-submitted field is fully validated before persistence; no malformed/protected value is stored
- Expected Immunefi impact: Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption
- Fast validation: validation table test: pass the crafted object, assert a field.Error is returned
