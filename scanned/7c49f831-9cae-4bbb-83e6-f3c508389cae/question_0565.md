# Q0565: policybased update in EscalationAllowed

## Question
Can an unprivileged attacker reaching `pkg/registry/rbac/escalation_check.go` via create/update of an RBAC or authorization object via the public kube-apiserver, supplying an update/patch that mutates an existing role's rules, cause `EscalationAllowed` to be exercised such that the policybased storage wrapper checks escalation on create but not on update/patch, allowing after-the-fact widening, breaking the invariant that a subject may only create/bind rules whose permissions it already holds (escalation & bind checks), and leading to Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)?

## Target
- File/function: `pkg/registry/rbac/escalation_check.go` -> `EscalationAllowed`
- Entrypoint: create/update of an RBAC or authorization object via the public kube-apiserver
- Attacker controls: an update/patch that mutates an existing role's rules
- Exploit idea: the policybased storage wrapper checks escalation on create but not on update/patch, allowing after-the-fact widening
- Invariant to test: a subject may only create/bind rules whose permissions it already holds (escalation & bind checks)
- Expected Immunefi impact: Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)
- Fast validation: integration/unit test: as a limited user create/patch the role/binding, assert escalation error
