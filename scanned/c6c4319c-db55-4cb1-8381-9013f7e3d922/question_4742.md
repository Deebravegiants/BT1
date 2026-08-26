# Q4742: expiry/nbf skew in unionAuthTokenHandler

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authentication/token/union/union.go` via HTTP request to kube-apiserver presenting a bearer token or client certificate, supplying a token with manipulated exp/nbf/iat claims, cause `unionAuthTokenHandler` to be exercised such that time-claim validation has an off-by-one or missing check, letting an expired or not-yet-valid token authenticate, breaking the invariant that only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged, and leading to Authentication bypass / identity forgery -> impersonation of another user or serviceaccount?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authentication/token/union/union.go` -> `unionAuthTokenHandler`
- Entrypoint: HTTP request to kube-apiserver presenting a bearer token or client certificate
- Attacker controls: a token with manipulated exp/nbf/iat claims
- Exploit idea: time-claim validation has an off-by-one or missing check, letting an expired or not-yet-valid token authenticate
- Invariant to test: only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged
- Expected Immunefi impact: Authentication bypass / identity forgery -> impersonation of another user or serviceaccount
- Fast validation: unit test: feed the crafted token/cert to the authenticator, assert failure or correct identity
