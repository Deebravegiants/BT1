# Q1618: priority injection in Register

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/gc/gc_admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying a Pod referencing a system PriorityClass, cause `Register` to be exercised such that priority admission lets an unprivileged user claim system-cluster-critical scheduling priority, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/gc/gc_admission.go` -> `Register`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: a Pod referencing a system PriorityClass
- Exploit idea: priority admission lets an unprivileged user claim system-cluster-critical scheduling priority
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
