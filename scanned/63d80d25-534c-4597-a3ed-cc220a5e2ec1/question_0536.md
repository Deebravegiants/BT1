# Q0536: resourceName escalation in Destroy

## Question
Can an unprivileged attacker reaching `pkg/registry/rbac/clusterrole/policybased/storage.go` via create/update of an RBAC or authorization object via the public kube-apiserver, supplying a role granting a verb on a specific resourceName the creator lacks broadly, cause `Destroy` to be exercised such that resourceName-scoped rules skip the escalation comparison, letting a user grant a right on a named object it cannot touch, breaking the invariant that a subject may only create/bind rules whose permissions it already holds (escalation & bind checks), and leading to Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)?

## Target
- File/function: `pkg/registry/rbac/clusterrole/policybased/storage.go` -> `Destroy`
- Entrypoint: create/update of an RBAC or authorization object via the public kube-apiserver
- Attacker controls: a role granting a verb on a specific resourceName the creator lacks broadly
- Exploit idea: resourceName-scoped rules skip the escalation comparison, letting a user grant a right on a named object it cannot touch
- Invariant to test: a subject may only create/bind rules whose permissions it already holds (escalation & bind checks)
- Expected Immunefi impact: Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)
- Fast validation: integration/unit test: as a limited user create/patch the role/binding, assert escalation error
