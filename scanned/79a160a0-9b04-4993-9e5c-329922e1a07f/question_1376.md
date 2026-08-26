# Q1376: self-node spoof in NodeAuthorizer

## Question
Can an unprivileged attacker reaching `plugin/pkg/auth/authorizer/node/node_authorizer.go` via kube-apiserver authorization: an authenticated API request evaluated by the Node authorizer graph, supplying a request whose node name is derived from attacker-influenced spec fields, cause `NodeAuthorizer` to be exercised such that node identity used for graph lookup is taken from a field the attacker can set, breaking the invariant that a node identity may only reach objects its graph edges authorize; no cross-node or unrelated-secret reach, and leading to Node authorizer scope bypass -> unauthorized access to secrets/objects of other nodes (authz bypass / privilege escalation)?

## Target
- File/function: `plugin/pkg/auth/authorizer/node/node_authorizer.go` -> `NodeAuthorizer`
- Entrypoint: kube-apiserver authorization: an authenticated API request evaluated by the Node authorizer graph
- Attacker controls: a request whose node name is derived from attacker-influenced spec fields
- Exploit idea: node identity used for graph lookup is taken from a field the attacker can set
- Invariant to test: a node identity may only reach objects its graph edges authorize; no cross-node or unrelated-secret reach
- Expected Immunefi impact: Node authorizer scope bypass -> unauthorized access to secrets/objects of other nodes (authz bypass / privilege escalation)
- Fast validation: unit test on the node graph: add attacker pod edge, call authorizer, assert secret read is denied
