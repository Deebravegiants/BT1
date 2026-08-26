# Q0362: union short-circuit in ConditionsAwareAuthorize

## Question
Can an unprivileged attacker reaching `plugin/pkg/auth/authorizer/rbac/rbac.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying concurrent requests hitting a union of authorizers, cause `ConditionsAwareAuthorize` to be exercised such that one authorizer's error/no-opinion is treated as allow, or ordering lets a deny be overridden by a later allow, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `plugin/pkg/auth/authorizer/rbac/rbac.go` -> `ConditionsAwareAuthorize`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: concurrent requests hitting a union of authorizers
- Exploit idea: one authorizer's error/no-opinion is treated as allow, or ordering lets a deny be overridden by a later allow
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
