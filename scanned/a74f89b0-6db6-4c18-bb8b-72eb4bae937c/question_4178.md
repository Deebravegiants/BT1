# Q4178: claim forgery in legacyValidator

## Question
Can an unprivileged attacker reaching `pkg/serviceaccount/legacy.go` via TokenRequest / projected serviceaccount token presented to kube-apiserver, supplying a TokenRequest with attacker-influenced bound-object refs, cause `legacyValidator` to be exercised such that claim construction trusts a spec field so the issued token names a serviceaccount/pod the caller does not own, breaking the invariant that a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused, and leading to ServiceAccount token forgery/confusion -> impersonation and privilege escalation?

## Target
- File/function: `pkg/serviceaccount/legacy.go` -> `legacyValidator`
- Entrypoint: TokenRequest / projected serviceaccount token presented to kube-apiserver
- Attacker controls: a TokenRequest with attacker-influenced bound-object refs
- Exploit idea: claim construction trusts a spec field so the issued token names a serviceaccount/pod the caller does not own
- Invariant to test: a token authenticates exactly the issued serviceaccount, audience and bound object, and cannot be replayed/confused
- Expected Immunefi impact: ServiceAccount token forgery/confusion -> impersonation and privilege escalation
- Fast validation: unit test: issue via the claims/jwt path, validate, assert audience/binding/expiry enforced
