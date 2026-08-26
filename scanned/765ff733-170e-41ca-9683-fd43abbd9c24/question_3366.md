# Q3366: name from body in applyAdmission

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/patch.go` via REST create/update/patch/get request handled by the kube-apiserver endpoints layer, supplying a create where the object name is taken from the body not the path, cause `applyAdmission` to be exercised such that name resolution trusts the body, letting the object land under a name the user is not authorized for, breaking the invariant that the object is created/read under exactly the namespace and name the requester is authorized for, and leading to Scope/namespace confusion -> cross-namespace unauthorized read or write?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/patch.go` -> `applyAdmission`
- Entrypoint: REST create/update/patch/get request handled by the kube-apiserver endpoints layer
- Attacker controls: a create where the object name is taken from the body not the path
- Exploit idea: name resolution trusts the body, letting the object land under a name the user is not authorized for
- Invariant to test: the object is created/read under exactly the namespace and name the requester is authorized for
- Expected Immunefi impact: Scope/namespace confusion -> cross-namespace unauthorized read or write
- Fast validation: endpoints handler test: issue the request, assert scope/name resolves to the authorized target
