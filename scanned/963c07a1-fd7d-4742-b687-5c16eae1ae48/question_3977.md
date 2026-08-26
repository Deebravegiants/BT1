# Q3977: namespace scope leak in has

## Question
Can an unprivileged attacker reaching `pkg/registry/rbac/validation/rule.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying a namespaced request with empty/`*` namespace in the bound rule, cause `has` to be exercised such that namespace matching treats empty as all-namespaces, extending a namespaced grant cluster-wide, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `pkg/registry/rbac/validation/rule.go` -> `has`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: a namespaced request with empty/`*` namespace in the bound rule
- Exploit idea: namespace matching treats empty as all-namespaces, extending a namespaced grant cluster-wide
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
