# Q0765: resourceName bypass in GetRole

## Question
Can an unprivileged attacker reaching `plugin/pkg/auth/authorizer/rbac/rbac.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying a request whose object name differs only by trailing slash, case, or unicode, cause `GetRole` to be exercised such that resourceName restriction is compared without normalization so a near-miss name slips past a name-scoped grant, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `plugin/pkg/auth/authorizer/rbac/rbac.go` -> `GetRole`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: a request whose object name differs only by trailing slash, case, or unicode
- Exploit idea: resourceName restriction is compared without normalization so a near-miss name slips past a name-scoped grant
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
