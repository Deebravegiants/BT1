# Q3569: priority injection in convert

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/security/podsecurity/admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying a Pod referencing a system PriorityClass, cause `convert` to be exercised such that priority admission lets an unprivileged user claim system-cluster-critical scheduling priority, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/security/podsecurity/admission.go` -> `convert`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: a Pod referencing a system PriorityClass
- Exploit idea: priority admission lets an unprivileged user claim system-cluster-critical scheduling priority
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
