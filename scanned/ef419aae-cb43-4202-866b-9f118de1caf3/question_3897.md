# Q3897: owner reference in getNamespaceDefaultTolerations

## Question
Can an unprivileged attacker reaching `plugin/pkg/admission/podtolerationrestriction/admission.go` via create/update/patch request passing through the kube-apiserver admission chain, supplying an object with a crafted ownerReference to another user's object, cause `getNamespaceDefaultTolerations` to be exercised such that garbage-collection admission allows adopting/deleting objects the user does not own, breaking the invariant that protected fields and identities cannot be set/altered by a requester lacking authority, and leading to Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)?

## Target
- File/function: `plugin/pkg/admission/podtolerationrestriction/admission.go` -> `getNamespaceDefaultTolerations`
- Entrypoint: create/update/patch request passing through the kube-apiserver admission chain
- Attacker controls: an object with a crafted ownerReference to another user's object
- Exploit idea: garbage-collection admission allows adopting/deleting objects the user does not own
- Invariant to test: protected fields and identities cannot be set/altered by a requester lacking authority
- Expected Immunefi impact: Admission bypass -> control of a protected field/identity (privilege escalation / isolation escape)
- Fast validation: admission unit test: submit the object, assert the protected field is rejected/overwritten
