# Q4343: graph edge injection in newNamedVertex

## Question
Can an unprivileged attacker reaching `plugin/pkg/auth/authorizer/node/graph.go` via kube-apiserver authorization: an authenticated API request evaluated by the Node authorizer graph, supplying a Pod spec referencing secrets/configmaps/PVCs of another node's workloads, cause `newNamedVertex` to be exercised such that node authorizer graph edges let a node reach a secret it should not, via an attacker-planted reference, breaking the invariant that a node identity may only reach objects its graph edges authorize; no cross-node or unrelated-secret reach, and leading to Node authorizer scope bypass -> unauthorized access to secrets/objects of other nodes (authz bypass / privilege escalation)?

## Target
- File/function: `plugin/pkg/auth/authorizer/node/graph.go` -> `newNamedVertex`
- Entrypoint: kube-apiserver authorization: an authenticated API request evaluated by the Node authorizer graph
- Attacker controls: a Pod spec referencing secrets/configmaps/PVCs of another node's workloads
- Exploit idea: node authorizer graph edges let a node reach a secret it should not, via an attacker-planted reference
- Invariant to test: a node identity may only reach objects its graph edges authorize; no cross-node or unrelated-secret reach
- Expected Immunefi impact: Node authorizer scope bypass -> unauthorized access to secrets/objects of other nodes (authz bypass / privilege escalation)
- Fast validation: unit test on the node graph: add attacker pod edge, call authorizer, assert secret read is denied
