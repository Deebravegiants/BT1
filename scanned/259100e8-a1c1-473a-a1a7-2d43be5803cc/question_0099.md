# Q0099: immutable field in AllowPrivilegeEscalation

## Question
Can an unprivileged attacker reaching `pkg/securitycontext/accessors.go` via create/update request body validated by the kube-apiserver registry, supplying an update mutating a field validation should freeze, cause `AllowPrivilegeEscalation` to be exercised such that update validation omits the immutability check, allowing mutation of a security-relevant field, breaking the invariant that every user-submitted field is fully validated before persistence; no malformed/protected value is stored, and leading to Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption?

## Target
- File/function: `pkg/securitycontext/accessors.go` -> `AllowPrivilegeEscalation`
- Entrypoint: create/update request body validated by the kube-apiserver registry
- Attacker controls: an update mutating a field validation should freeze
- Exploit idea: update validation omits the immutability check, allowing mutation of a security-relevant field
- Invariant to test: every user-submitted field is fully validated before persistence; no malformed/protected value is stored
- Expected Immunefi impact: Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption
- Fast validation: validation table test: pass the crafted object, assert a field.Error is returned
