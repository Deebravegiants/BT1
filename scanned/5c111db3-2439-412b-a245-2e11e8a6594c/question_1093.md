# Q1093: aggregation rule in NamespaceScoped

## Question
Can an unprivileged attacker reaching `pkg/registry/rbac/rolebinding/policybased/storage.go` via create/update of an RBAC or authorization object via the public kube-apiserver, supplying a ClusterRole with aggregationRule label selectors, cause `NamespaceScoped` to be exercised such that aggregated rules are compiled in without re-running escalation checks, pulling in privileges the creator lacks, breaking the invariant that a subject may only create/bind rules whose permissions it already holds (escalation & bind checks), and leading to Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)?

## Target
- File/function: `pkg/registry/rbac/rolebinding/policybased/storage.go` -> `NamespaceScoped`
- Entrypoint: create/update of an RBAC or authorization object via the public kube-apiserver
- Attacker controls: a ClusterRole with aggregationRule label selectors
- Exploit idea: aggregated rules are compiled in without re-running escalation checks, pulling in privileges the creator lacks
- Invariant to test: a subject may only create/bind rules whose permissions it already holds (escalation & bind checks)
- Expected Immunefi impact: Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)
- Fast validation: integration/unit test: as a limited user create/patch the role/binding, assert escalation error
