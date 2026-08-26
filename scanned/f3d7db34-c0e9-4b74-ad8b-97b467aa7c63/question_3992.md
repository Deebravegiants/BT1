# Q3992: expiry override in hasCorrectIssuer

## Question
Can an unprivileged attacker reaching `pkg/serviceaccount/jwt.go` via TokenRequest / projected serviceaccount token presented to kube-apiserver, supplying a TokenRequest with an oversized/negative expirationSeconds, cause `hasCorrectIssuer` to be exercised such that expiration clamping is bypassed, minting a long-lived or non-expiring token, breaking the invariant that a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused, and leading to ServiceAccount token forgery/confusion -> impersonation and privilege escalation?

## Target
- File/function: `pkg/serviceaccount/jwt.go` -> `hasCorrectIssuer`
- Entrypoint: TokenRequest / projected serviceaccount token presented to kube-apiserver
- Attacker controls: a TokenRequest with an oversized/negative expirationSeconds
- Exploit idea: expiration clamping is bypassed, minting a long-lived or non-expiring token
- Invariant to test: a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused
- Expected Immunefi impact: ServiceAccount token forgery/confusion -> impersonation and privilege escalation
- Fast validation: unit test: issue via the claims/jwt path, validate, assert audience/binding/expiry enforced
