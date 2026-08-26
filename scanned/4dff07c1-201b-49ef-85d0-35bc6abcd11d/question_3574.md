# Q3574: bind check bypass in convertToUserInfoExtra

## Question
Can an unprivileged attacker reaching `pkg/registry/authorization/util/helpers.go` via create/update of an RBAC or authorization object via the public kube-apiserver, supplying a RoleBinding/ClusterRoleBinding to a high-privilege role, cause `convertToUserInfoExtra` to be exercised such that the bind authorization check is skipped or mis-scoped, letting a user bind a role it cannot use, breaking the invariant that a subject may only create/bind rules whose permissions it already holds (escalation & bind checks), and leading to Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)?

## Target
- File/function: `pkg/registry/authorization/util/helpers.go` -> `convertToUserInfoExtra`
- Entrypoint: create/update of an RBAC or authorization object via the public kube-apiserver
- Attacker controls: a RoleBinding/ClusterRoleBinding to a high-privilege role
- Exploit idea: the bind authorization check is skipped or mis-scoped, letting a user bind a role it cannot use
- Invariant to test: a subject may only create/bind rules whose permissions it already holds (escalation & bind checks)
- Expected Immunefi impact: Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)
- Fast validation: integration/unit test: as a limited user create/patch the role/binding, assert escalation error
