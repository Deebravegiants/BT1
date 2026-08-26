# Q3174: stale edge in addPV

## Question
Can an unprivileged attacker reaching `plugin/pkg/auth/authorizer/node/graph_populator.go` via kube-apiserver authorization: an authenticated API request evaluated by the Node authorizer graph, supplying rapid create/delete of pods referencing a target secret, cause `addPV` to be exercised such that graph edges are added but not removed atomically, leaving a node authorized to read a secret after detachment, breaking the invariant that a node identity may only reach objects its graph edges authorize; no cross-node or unrelated-secret reach, and leading to Node authorizer scope bypass -> unauthorized access to secrets/objects of other nodes (authz bypass / privilege escalation)?

## Target
- File/function: `plugin/pkg/auth/authorizer/node/graph_populator.go` -> `addPV`
- Entrypoint: kube-apiserver authorization: an authenticated API request evaluated by the Node authorizer graph
- Attacker controls: rapid create/delete of pods referencing a target secret
- Exploit idea: graph edges are added but not removed atomically, leaving a node authorized to read a secret after detachment
- Invariant to test: a node identity may only reach objects its graph edges authorize; no cross-node or unrelated-secret reach
- Expected Immunefi impact: Node authorizer scope bypass -> unauthorized access to secrets/objects of other nodes (authz bypass / privilege escalation)
- Fast validation: unit test on the node graph: add attacker pod edge, call authorizer, assert secret read is denied
