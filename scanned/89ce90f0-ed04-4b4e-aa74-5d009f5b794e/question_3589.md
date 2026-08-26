# Q3589: subresource routing in createHandler

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/create.go` via REST create/update/patch/get request handled by the kube-apiserver endpoints layer, supplying a request whose subresource path is ambiguous, cause `createHandler` to be exercised such that the namer maps the request to a different resource/subresource than authorization evaluated, breaking the invariant that the object is created/read under exactly the namespace and name the requester is authorized for, and leading to Scope/namespace confusion -> cross-namespace unauthorized read or write?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/create.go` -> `createHandler`
- Entrypoint: REST create/update/patch/get request handled by the kube-apiserver endpoints layer
- Attacker controls: a request whose subresource path is ambiguous
- Exploit idea: the namer maps the request to a different resource/subresource than authorization evaluated
- Invariant to test: the object is created/read under exactly the namespace and name the requester is authorized for
- Expected Immunefi impact: Scope/namespace confusion -> cross-namespace unauthorized read or write
- Fast validation: endpoints handler test: issue the request, assert scope/name resolves to the authorized target
