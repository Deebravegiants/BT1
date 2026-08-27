### Title
No vulnerability found — `EscalationAllowed` group matching is exact-match only

### Summary
`EscalationAllowed` in `pkg/registry/rbac/escalation_check.go` compares each of the user's groups to `user.SystemPrivilegedGroup` ("system:masters") using Go's native `==` string equality operator, which is inherently case-sensitive and requires an exact match. There is no case-folding, prefix, or substring logic anywhere in this function or in the group-population path that would let a group literally named `system:masters-lookalike` or `System:Masters` be treated as `system:masters`.

### Finding Description [1](#0-0) 
The loop iterates `u.GetGroups()` and checks `group == user.SystemPrivilegedGroup`. Go's `==` on strings is byte-for-byte comparison; `"System:Masters" == "system:masters"` and `"system:masters-lookalike" == "system:masters"` both evaluate to `false`. No normalization (`strings.ToLower`, `strings.EqualFold`, `strings.HasPrefix/Contains`) is applied to group names before or during this comparison, and no such normalization was found in the authentication/group-mapping code searched (`staging/src/k8s.io/apiserver/pkg/authentication/...`). Therefore an attacker whose external IdP maps them into a group named `system:masters-lookalike` or the case-variant `System:Masters` would not match the exact string `system:masters` and `EscalationAllowed` would correctly return `false`.

### Impact Explanation
None. The exact-match design is the correct and intended behavior — it is what prevents a lookalike/case-variant group name from being treated as the highly privileged `system:masters` group. There is no case-insensitive or substring bypass.

### Likelihood Explanation
Not applicable; no exploitable condition exists given the current implementation.

### Recommendation
No change needed. If desired for defense-in-depth/documentation, the comment could explicitly note that group comparison is intentionally case-sensitive/exact, but this is not a security requirement.

### Proof of Concept
A table test on `EscalationAllowed` with `context` populated via `genericapirequest.WithUser` for user with groups `["System:Masters"]` and separately `["system:masters-lookalike"]` would assert the function returns `false` in both cases, and only `["system:masters"]` returns `true` — confirming the existing exact-match `==` semantics already provide this guarantee with no code change required.

### Citations

**File:** pkg/registry/rbac/escalation_check.go (L40-44)
```go
	for _, group := range u.GetGroups() {
		if group == user.SystemPrivilegedGroup {
			return true
		}
	}
```
