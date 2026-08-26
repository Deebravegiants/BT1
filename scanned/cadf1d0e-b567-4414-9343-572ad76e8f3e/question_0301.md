# Q0301: subresource split in ClusterRoleBindingLister

## Question
Can an unprivileged attacker reaching `plugin/pkg/auth/authorizer/rbac/rbac.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying a request to a subresource (`/status`,`/scale`,`/exec`), cause `ClusterRoleBindingLister` to be exercised such that the authorizer matches the parent resource rule to a subresource (or vice versa), leaking a verb never granted, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `plugin/pkg/auth/authorizer/rbac/rbac.go` -> `ClusterRoleBindingLister`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: a request to a subresource (`/status`,`/scale`,`/exec`)
- Exploit idea: the authorizer matches the parent resource rule to a subresource (or vice versa), leaking a verb never granted
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
