# Q0950: legacy token reuse in JWTTokenGenerator

## Question
Can an unprivileged attacker reaching `pkg/serviceaccount/jwt.go` via TokenRequest / projected serviceaccount token presented to kube-apiserver, supplying a legacy (non-expiring) serviceaccount token from another namespace, cause `JWTTokenGenerator` to be exercised such that legacy token validation resolves the SA/namespace from an attacker-supplied field, enabling cross-namespace impersonation, breaking the invariant that a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused, and leading to ServiceAccount token forgery/confusion -> impersonation and privilege escalation?

## Target
- File/function: `pkg/serviceaccount/jwt.go` -> `JWTTokenGenerator`
- Entrypoint: TokenRequest / projected serviceaccount token presented to kube-apiserver
- Attacker controls: a legacy (non-expiring) serviceaccount token from another namespace
- Exploit idea: legacy token validation resolves the SA/namespace from an attacker-supplied field, enabling cross-namespace impersonation
- Invariant to test: a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused
- Expected Immunefi impact: ServiceAccount token forgery/confusion -> impersonation and privilege escalation
- Fast validation: unit test: issue via the claims/jwt path, validate, assert audience/binding/expiry enforced
