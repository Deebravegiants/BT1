# Q4367: update path gap in nodeAllocatableMappedResourcesEqual

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/noderestriction/admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying an update/patch that changes a field the plugin only guards on create, cause `nodeAllocatableMappedResourcesEqual` to be exercised such that the plugin's create-only guard lets the field be mutated later via update/patch, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/noderestriction/admission.go` -> `nodeAllocatableMappedResourcesEqual`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: an update/patch that changes a field the plugin only guards on create
- Exploit idea: the plugin's create-only guard lets the field be mutated later via update/patch
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
