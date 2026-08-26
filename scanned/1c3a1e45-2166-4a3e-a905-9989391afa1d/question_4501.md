# Q4501: field set bypass in podResourcesOptions

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/limitranger/admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying a create/update setting a protected field (nodeName, serviceAccountName, priorityClassName, tolerations), cause `podResourcesOptions` to be exercised such that the admission plugin fails to reject or overwrite an attacker-set protected field, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/limitranger/admission.go` -> `podResourcesOptions`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: a create/update setting a protected field (nodeName, serviceAccountName, priorityClassName, tolerations)
- Exploit idea: the admission plugin fails to reject or overwrite an attacker-set protected field
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
