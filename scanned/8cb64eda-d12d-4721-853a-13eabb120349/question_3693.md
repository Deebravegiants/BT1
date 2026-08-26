# Q3693: priority injection in doWork

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying a Pod referencing a system PriorityClass, cause `doWork` to be exercised such that priority admission lets an unprivileged user claim system-cluster-critical scheduling priority, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go` -> `doWork`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: a Pod referencing a system PriorityClass
- Exploit idea: priority admission lets an unprivileged user claim system-cluster-critical scheduling priority
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
