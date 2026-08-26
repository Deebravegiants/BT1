# Q3586: generateName collision in createHandler

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/create.go` via REST create/update/patch/get request handled by the kube-apiserver endpoints layer, supplying rapid creates using generateName, cause `createHandler` to be exercised such that name generation races produce a collision or predictable name a user can target, breaking the invariant that the object is created/read under exactly the namespace and name the requester is authorized for, and leading to Scope/namespace confusion -> cross-namespace unauthorized read or write?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/create.go` -> `createHandler`
- Entrypoint: REST create/update/patch/get request handled by the kube-apiserver endpoints layer
- Attacker controls: rapid creates using generateName
- Exploit idea: name generation races produce a collision or predictable name a user can target
- Invariant to test: the object is created/read under exactly the namespace and name the requester is authorized for
- Expected Immunefi impact: Scope/namespace confusion -> cross-namespace unauthorized read or write
- Fast validation: endpoints handler test: issue the request, assert scope/name resolves to the authorized target
