# Q0139: anonymous fallthrough in AuthenticateRequest

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authentication/request/union/union.go` via HTTP request to kube-apiserver presenting a bearer token or client certificate, supplying a request that fails token auth but reaches anonymous, cause `AuthenticateRequest` to be exercised such that a failed authenticator falls through to anonymous with elevated (non-anonymous) attributes, breaking the invariant that only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged, and leading to Authentication bypass / identity forgery -> impersonation of another user or serviceaccount?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authentication/request/union/union.go` -> `AuthenticateRequest`
- Entrypoint: HTTP request to kube-apiserver presenting a bearer token or client certificate
- Attacker controls: a request that fails token auth but reaches anonymous
- Exploit idea: a failed authenticator falls through to anonymous with elevated (non-anonymous) attributes
- Invariant to test: only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged
- Expected Immunefi impact: Authentication bypass / identity forgery -> impersonation of another user or serviceaccount
- Fast validation: unit test: feed the crafted token/cert to the authenticator, assert failure or correct identity
