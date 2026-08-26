# Q3883: bound-object mismatch in getMutatingWebhookMeta

## Question
Can an unprivileged attacker reaching `pkg/serviceaccount/claims.go` via TokenRequest / projected serviceaccount token presented to kube-apiserver, supplying a token bound to a pod/secret then presented after the object changes, cause `getMutatingWebhookMeta` to be exercised such that bound-object invalidation is missed, so a stale token still authenticates the serviceaccount, breaking the invariant that a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused, and leading to ServiceAccount token forgery/confusion -> impersonation and privilege escalation?

## Target
- File/function: `pkg/serviceaccount/claims.go` -> `getMutatingWebhookMeta`
- Entrypoint: TokenRequest / projected serviceaccount token presented to kube-apiserver
- Attacker controls: a token bound to a pod/secret then presented after the object changes
- Exploit idea: bound-object invalidation is missed, so a stale token still authenticates the serviceaccount
- Invariant to test: a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused
- Expected Immunefi impact: ServiceAccount token forgery/confusion -> impersonation and privilege escalation
- Fast validation: unit test: issue via the claims/jwt path, validate, assert audience/binding/expiry enforced
