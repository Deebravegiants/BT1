# Q0097: cross-field inconsistency in AllowPrivilegeEscalation

## Question
Can an unprivileged attacker reaching `pkg/securitycontext/accessors.go` via create/update request body validated by the kube-apiserver registry, supplying two related fields set to contradictory values, cause `AllowPrivilegeEscalation` to be exercised such that validation checks each field alone, persisting an inconsistent pair a consumer trusts, breaking the invariant that every user-submitted field is fully validated before persistence; no malformed/protected value is stored, and leading to Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption?

## Target
- File/function: `pkg/securitycontext/accessors.go` -> `AllowPrivilegeEscalation`
- Entrypoint: create/update request body validated by the kube-apiserver registry
- Attacker controls: two related fields set to contradictory values
- Exploit idea: validation checks each field alone, persisting an inconsistent pair a consumer trusts
- Invariant to test: every user-submitted field is fully validated before persistence; no malformed/protected value is stored
- Expected Immunefi impact: Validation bypass -> invalid/protected spec persisted, downstream injection or cross-user corruption
- Fast validation: validation table test: pass the crafted object, assert a field.Error is returned
