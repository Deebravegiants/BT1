# Q1806: audience widening in ServiceAccountTokenGetter

## Question
Can an unprivileged attacker reaching `pkg/serviceaccount/jwt.go` via TokenRequest / projected serviceaccount token presented to kube-apiserver, supplying a token requested with multiple/empty audiences, cause `ServiceAccountTokenGetter` to be exercised such that audience handling widens the token's validity beyond the requested service, breaking the invariant that a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused, and leading to ServiceAccount token forgery/confusion -> impersonation and privilege escalation?

## Target
- File/function: `pkg/serviceaccount/jwt.go` -> `ServiceAccountTokenGetter`
- Entrypoint: TokenRequest / projected serviceaccount token presented to kube-apiserver
- Attacker controls: a token requested with multiple/empty audiences
- Exploit idea: audience handling widens the token's validity beyond the requested service
- Invariant to test: a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused
- Expected Immunefi impact: ServiceAccount token forgery/confusion -> impersonation and privilege escalation
- Fast validation: unit test: issue via the claims/jwt path, validate, assert audience/binding/expiry enforced
