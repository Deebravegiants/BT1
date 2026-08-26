# Q0178: x509 chain confusion in Authenticator

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authentication/request/bearertoken/bearertoken.go` via HTTP request to kube-apiserver presenting a bearer token or client certificate, supplying a client cert with crafted CN/Organization or SAN, cause `Authenticator` to be exercised such that x509 identity extraction uses a field the attacker controls, or accepts a cert from a non-client CA path, breaking the invariant that only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged, and leading to Authentication bypass / identity forgery -> impersonation of another user or serviceaccount?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authentication/request/bearertoken/bearertoken.go` -> `Authenticator`
- Entrypoint: HTTP request to kube-apiserver presenting a bearer token or client certificate
- Attacker controls: a client cert with crafted CN/Organization or SAN
- Exploit idea: x509 identity extraction uses a field the attacker controls, or accepts a cert from a non-client CA path
- Invariant to test: only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged
- Expected Immunefi impact: Authentication bypass / identity forgery -> impersonation of another user or serviceaccount
- Fast validation: unit test: feed the crafted token/cert to the authenticator, assert failure or correct identity
