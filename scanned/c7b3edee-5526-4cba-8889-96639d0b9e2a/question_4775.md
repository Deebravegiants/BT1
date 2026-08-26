# Q4775: dry-run/patch bypass in updateToCreateOptions

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/update.go` via REST create/update/patch/get request handled by the kube-apiserver endpoints layer, supplying a patch or server-side-apply with a crafted fieldManager/path, cause `updateToCreateOptions` to be exercised such that the patch merge sets a field that a direct create would have had rejected, breaking the invariant that the object is created/read under exactly the namespace and name the requester is authorized for, and leading to Scope/namespace confusion -> cross-namespace unauthorized read or write?

## Target
- File/function: `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/update.go` -> `updateToCreateOptions`
- Entrypoint: REST create/update/patch/get request handled by the kube-apiserver endpoints layer
- Attacker controls: a patch or server-side-apply with a crafted fieldManager/path
- Exploit idea: the patch merge sets a field that a direct create would have had rejected
- Invariant to test: the object is created/read under exactly the namespace and name the requester is authorized for
- Expected Immunefi impact: Scope/namespace confusion -> cross-namespace unauthorized read or write
- Fast validation: endpoints handler test: issue the request, assert scope/name resolves to the authorized target
