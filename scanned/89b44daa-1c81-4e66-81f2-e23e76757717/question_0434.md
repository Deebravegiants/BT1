# Q0434: namespace mismatch in Create

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/create.go` via REST create/update/patch/get request handled by the kube-apiserver endpoints layer, supplying a request whose URL namespace differs from the object body namespace, cause `Create` to be exercised such that the handler resolves scope from one source and authorizes on the other, enabling cross-namespace write, breaking the invariant that the object is created/read under exactly the namespace and name the requester is authorized for, and leading to Scope/namespace confusion -> cross-namespace unauthorized read or write?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/create.go` -> `Create`
- Entrypoint: REST create/update/patch/get request handled by the kube-apiserver endpoints layer
- Attacker controls: a request whose URL namespace differs from the object body namespace
- Exploit idea: the handler resolves scope from one source and authorizes on the other, enabling cross-namespace write
- Invariant to test: the object is created/read under exactly the namespace and name the requester is authorized for
- Expected Immunefi impact: Scope/namespace confusion -> cross-namespace unauthorized read or write
- Fast validation: endpoints handler test: issue the request, assert scope/name resolves to the authorized target
