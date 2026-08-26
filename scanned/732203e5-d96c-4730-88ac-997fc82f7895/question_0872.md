# Q0872: non-resource path in IsError

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authorization/authorizer/evaluate.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying a crafted non-resource URL path with `..`, double slash, or trailing segment, cause `IsError` to be exercised such that non-resource-URL matching normalizes differently from routing, granting a path the rule intended to deny, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authorization/authorizer/evaluate.go` -> `IsError`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: a crafted non-resource URL path with `..`, double slash, or trailing segment
- Exploit idea: non-resource-URL matching normalizes differently from routing, granting a path the rule intended to deny
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
