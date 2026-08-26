# Q1322: token confusion in NewStaticVerifierFromFile

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/authentication/request/x509/verify_options.go` via HTTP request to kube-apiserver presenting a bearer token or client certificate, supplying a bearer token whose format overlaps two authenticators, cause `NewStaticVerifierFromFile` to be exercised such that authenticator union tries them in an order that lets a serviceaccount token be accepted as a different identity, breaking the invariant that only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged, and leading to Authentication bypass / identity forgery -> impersonation of another user or serviceaccount?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/authentication/request/x509/verify_options.go` -> `NewStaticVerifierFromFile`
- Entrypoint: HTTP request to kube-apiserver presenting a bearer token or client certificate
- Attacker controls: a bearer token whose format overlaps two authenticators
- Exploit idea: authenticator union tries them in an order that lets a serviceaccount token be accepted as a different identity
- Invariant to test: only a validly issued, unexpired, correctly-audienced credential authenticates; identity/groups cannot be forged
- Expected Immunefi impact: Authentication bypass / identity forgery -> impersonation of another user or serviceaccount
- Fast validation: unit test: feed the crafted token/cert to the authenticator, assert failure or correct identity
