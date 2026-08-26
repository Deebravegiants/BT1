# Q1005: cache poisoning in MakeGroupNames

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authentication/serviceaccount/util.go` via HTTP request to kube-apiserver presenting a bearer token or client certificate, supplying repeated tokens hitting the token cache, cause `MakeGroupNames` to be exercised such that the token cache keys on a value that collides, returning another principal's cached authentication result, breaking the invariant that only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged, and leading to Authentication bypass / identity forgery -> impersonation of another user or serviceaccount?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authentication/serviceaccount/util.go` -> `MakeGroupNames`
- Entrypoint: HTTP request to kube-apiserver presenting a bearer token or client certificate
- Attacker controls: repeated tokens hitting the token cache
- Exploit idea: the token cache keys on a value that collides, returning another principal's cached authentication result
- Invariant to test: only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged
- Expected Immunefi impact: Authentication bypass / identity forgery -> impersonation of another user or serviceaccount
- Fast validation: unit test: feed the crafted token/cert to the authenticator, assert failure or correct identity
