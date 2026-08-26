# Q1355: apiGroup confusion in NewTestRuleResolver

## Question
Can an unprivileged attacker reaching `pkg/registry/rbac/validation/rule.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying a rule referencing an aliased or empty apiGroup, cause `NewTestRuleResolver` to be exercised such that apiGroup comparison is case/format-insensitive or empty-group is treated as match-all, granting cross-group access, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `pkg/registry/rbac/validation/rule.go` -> `NewTestRuleResolver`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: a rule referencing an aliased or empty apiGroup
- Exploit idea: apiGroup comparison is case/format-insensitive or empty-group is treated as match-all, granting cross-group access
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
