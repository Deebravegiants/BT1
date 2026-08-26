# Q2033: escalation check bypass in StorageVersion

## Question
Can an unprivileged attacker reaching `pkg/registry/rbac/rolebinding/policybased/storage.go` via create/update of an RBAC or authorization object via the public kube-apiserver, supplying a Role/ClusterRole whose rules exceed the creator's own permissions, cause `StorageVersion` to be exercised such that the escalation check misses a rule variant (wildcard, aggregation, non-resource URL) so the user grants itself more than it holds, breaking the invariant that a subject may only create/bind rules whose permissions it already holds (escalation & bind checks), and leading to Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)?

## Target
- File/function: `pkg/registry/rbac/rolebinding/policybased/storage.go` -> `StorageVersion`
- Entrypoint: create/update of an RBAC or authorization object via the public kube-apiserver
- Attacker controls: a Role/ClusterRole whose rules exceed the creator's own permissions
- Exploit idea: the escalation check misses a rule variant (wildcard, aggregation, non-resource URL) so the user grants itself more than it holds
- Invariant to test: a subject may only create/bind rules whose permissions it already holds (escalation & bind checks)
- Expected Immunefi impact: Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)
- Fast validation: integration/unit test: as a limited user create/patch the role/binding, assert escalation error
