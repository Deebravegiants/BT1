# Q1153: audience bypass in NewAuthenticator

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authentication/request/anonymous/anonymous.go` via HTTP request to kube-apiserver presenting a bearer token or client certificate, supplying a projected token presented to an endpoint with a different audience, cause `NewAuthenticator` to be exercised such that audience validation is skipped or accepts an empty/extra audience, allowing token reuse across services, breaking the invariant that only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged, and leading to Authentication bypass / identity forgery -> impersonation of another user or serviceaccount?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authentication/request/anonymous/anonymous.go` -> `NewAuthenticator`
- Entrypoint: HTTP request to kube-apiserver presenting a bearer token or client certificate
- Attacker controls: a projected token presented to an endpoint with a different audience
- Exploit idea: audience validation is skipped or accepts an empty/extra audience, allowing token reuse across services
- Invariant to test: only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged
- Expected Immunefi impact: Authentication bypass / identity forgery -> impersonation of another user or serviceaccount
- Fast validation: unit test: feed the crafted token/cert to the authenticator, assert failure or correct identity
