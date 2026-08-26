# Q1857: subresource skip in SetExternalKubeClientSet

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/serviceaccount/admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying a write to a subresource (status/binding/ephemeralcontainers), cause `SetExternalKubeClientSet` to be exercised such that the admission plugin does not run on the subresource, so a protected field is set through it, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/serviceaccount/admission.go` -> `SetExternalKubeClientSet`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: a write to a subresource (status/binding/ephemeralcontainers)
- Exploit idea: the admission plugin does not run on the subresource, so a protected field is set through it
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
