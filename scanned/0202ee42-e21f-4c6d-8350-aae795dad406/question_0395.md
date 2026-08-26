# Q0395: SAR spoof in Create

## Question
Can an unprivileged attacker reaching `pkg/registry/authorization/localsubjectaccessreview/rest.go` via create/update of an RBAC or authorization object via the public kube-apiserver, supplying a SubjectAccessReview/SelfSubjectAccessReview with attacker-set user/groups, cause `Create` to be exercised such that the review authorizes against attacker-supplied identity fields instead of the caller's real identity, breaking the invariant that a subject may only create/bind rules whose permissions it already holds (escalation & bind checks), and leading to Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)?

## Target
- File/function: `pkg/registry/authorization/localsubjectaccessreview/rest.go` -> `Create`
- Entrypoint: create/update of an RBAC or authorization object via the public kube-apiserver
- Attacker controls: a SubjectAccessReview/SelfSubjectAccessReview with attacker-set user/groups
- Exploit idea: the review authorizes against attacker-supplied identity fields instead of the caller's real identity
- Invariant to test: a subject may only create/bind rules whose permissions it already holds (escalation & bind checks)
- Expected Immunefi impact: Privilege escalation -> subject grants itself rights it does not hold (cluster-admin / cross-namespace takeover)
- Fast validation: integration/unit test: as a limited user create/patch the role/binding, assert escalation error
