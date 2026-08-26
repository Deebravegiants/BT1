# Q0822: resourceName bypass in GetVerbs

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authorization/authorizer/rule.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying a request whose object name differs only by trailing slash, case, or unicode, cause `GetVerbs` to be exercised such that resourceName restriction is compared without normalization so a near-miss name slips past a name-scoped grant, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authorization/authorizer/rule.go` -> `GetVerbs`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: a request whose object name differs only by trailing slash, case, or unicode
- Exploit idea: resourceName restriction is compared without normalization so a near-miss name slips past a name-scoped grant
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
