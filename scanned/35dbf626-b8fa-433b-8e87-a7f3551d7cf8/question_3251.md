# Q3251: subresource skip in admitLease

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/noderestriction/admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying a write to a subresource (status/binding/ephemeralcontainers), cause `admitLease` to be exercised such that the admission plugin does not run on the subresource, so a protected field is set through it, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/noderestriction/admission.go` -> `admitLease`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: a write to a subresource (status/binding/ephemeralcontainers)
- Exploit idea: the admission plugin does not run on the subresource, so a protected field is set through it
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
