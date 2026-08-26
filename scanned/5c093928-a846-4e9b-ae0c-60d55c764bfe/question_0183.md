# Q0183: group injection in Authenticator

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authentication/request/x509/x509.go` via HTTP request to kube-apiserver presenting a bearer token or client certificate, supplying a token/cert whose subject encodes `system:` group prefixes, cause `Authenticator` to be exercised such that group extraction trusts an attacker-influenceable field, injecting privileged groups like system:masters, breaking the invariant that only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged, and leading to Authentication bypass / identity forgery -> impersonation of another user or serviceaccount?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authentication/request/x509/x509.go` -> `Authenticator`
- Entrypoint: HTTP request to kube-apiserver presenting a bearer token or client certificate
- Attacker controls: a token/cert whose subject encodes `system:` group prefixes
- Exploit idea: group extraction trusts an attacker-influenceable field, injecting privileged groups like system:masters
- Invariant to test: only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged
- Expected Immunefi impact: Authentication bypass / identity forgery -> impersonation of another user or serviceaccount
- Fast validation: unit test: feed the crafted token/cert to the authenticator, assert failure or correct identity
