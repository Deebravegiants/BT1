# Q4304: indirect reference in nameVertexMapping

## Question
Can an unprivileged attacker reaching `plugin/pkg/auth/authorizer/node/graph.go` via kube-apiserver authorization: an authenticated API request evaluated by the Node authorizer graph, supplying a pod referencing a configmap/PVC that transitively references another namespace's secret, cause `nameVertexMapping` to be exercised such that transitive edge population authorizes a node beyond its direct pod ownership, breaking the invariant that a node identity may only reach objects its graph edges authorize; no cross-node or unrelated-secret reach, and leading to Node authorizer scope bypass -> unauthorized access to secrets/objects of other nodes (authz bypass / privilege escalation)?

## Target
- File/function: `plugin/pkg/auth/authorizer/node/graph.go` -> `nameVertexMapping`
- Entrypoint: kube-apiserver authorization: an authenticated API request evaluated by the Node authorizer graph
- Attacker controls: a pod referencing a configmap/PVC that transitively references another namespace's secret
- Exploit idea: transitive edge population authorizes a node beyond its direct pod ownership
- Invariant to test: a node identity may only reach objects its graph edges authorize; no cross-node or unrelated-secret reach
- Expected Immunefi impact: Node authorizer scope bypass -> unauthorized access to secrets/objects of other nodes (authz bypass / privilege escalation)
- Fast validation: unit test on the node graph: add attacker pod edge, call authorizer, assert secret read is denied
