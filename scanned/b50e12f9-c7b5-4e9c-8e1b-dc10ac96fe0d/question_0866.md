# Q0866: owner reference in IsDefaultDeny

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying an object with a crafted ownerReference to another user's object, cause `IsDefaultDeny` to be exercised such that garbage-collection admission allows adopting/deleting objects the user does not own, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go` -> `IsDefaultDeny`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: an object with a crafted ownerReference to another user's object
- Exploit idea: garbage-collection admission allows adopting/deleting objects the user does not own
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
