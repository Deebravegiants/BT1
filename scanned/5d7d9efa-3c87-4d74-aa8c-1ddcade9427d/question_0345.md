# Q0345: wildcard verb match in ConditionEvaluationResultBoolean

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authorization/authorizer/evaluate.go` via kube-apiserver authorization of an authenticated (low-privilege) API request, supplying a Role with verb/resource wildcards or a subresource path like `pods/exec`, cause `ConditionEvaluationResultBoolean` to be exercised such that the rule-matching logic treats a wildcard, empty, or `*` field as matching a resource/verb the subject was not meant to reach, breaking the invariant that a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly, and leading to RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authorization/authorizer/evaluate.go` -> `ConditionEvaluationResultBoolean`
- Entrypoint: kube-apiserver authorization of an authenticated (low-privilege) API request
- Attacker controls: a Role with verb/resource wildcards or a subresource path like `pods/exec`
- Exploit idea: the rule-matching logic treats a wildcard, empty, or `*` field as matching a resource/verb the subject was not meant to reach
- Invariant to test: a request is authorized only if a bound RBAC rule (verb,resource,apiGroup,name,namespace,subresource) matches exactly
- Expected Immunefi impact: RBAC/authorization bypass -> unauthorized cross-tenant read or write (privilege escalation)
- Fast validation: table test: build the bound rule + request attributes, call the authorizer, assert Deny
