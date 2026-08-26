# Q2164: SA mount override in Validate

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/certificates/signing/admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying a Pod with an explicit serviceAccountName and token projection, cause `Validate` to be exercised such that serviceaccount admission mounts/binds a token for an SA the user cannot use, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/certificates/signing/admission.go` -> `Validate`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: a Pod with an explicit serviceAccountName and token projection
- Exploit idea: serviceaccount admission mounts/binds a token for an SA the user cannot use
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
