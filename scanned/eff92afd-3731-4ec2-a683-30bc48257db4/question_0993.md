# Q0993: non-resource path in ListRoleBindings

## Question
Can an unprivileged attacker reaching `plugin/pkg/auth/authorizer/rbac/rbac.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying a crafted non-resource URL path with `..`, double slash, or trailing segment, cause `ListRoleBindings` to be exercised such that non-resource-URL matching normalizes differently from routing, granting a path the rule intended to deny, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `plugin/pkg/auth/authorizer/rbac/rbac.go` -> `ListRoleBindings`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: a crafted non-resource URL path with `..`, double slash, or trailing segment
- Exploit idea: non-resource-URL matching normalizes differently from routing, granting a path the rule intended to deny
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
