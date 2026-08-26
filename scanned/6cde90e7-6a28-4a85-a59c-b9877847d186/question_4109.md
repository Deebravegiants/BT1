# Q4109: noderestriction spoof in isSupportedPodLevelResource

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/limitranger/admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying a node-scoped update (node status, pod status, labels), cause `isSupportedPodLevelResource` to be exercised such that the NodeRestriction guard mis-scopes the identity and permits a write reserved for a different node, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/limitranger/admission.go` -> `isSupportedPodLevelResource`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: a node-scoped update (node status, pod status, labels)
- Exploit idea: the NodeRestriction guard mis-scopes the identity and permits a write reserved for a different node
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
