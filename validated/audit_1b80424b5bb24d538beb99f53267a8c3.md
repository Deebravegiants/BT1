### Title
Attacker-supplied permissive toleration overrides namespace-mandated `NoExecute` default via `MergeTolerations` superset logic - (File: `plugin/pkg/admission/podtolerationrestriction/admission.go`)

### Summary
`PodTolerationRestriction.Admit` merges the pod's own tolerations with the namespace-mandated default tolerations using `tolerations.MergeTolerations`, which discards any toleration that is a "subset" of another. Because `isSuperset` treats a toleration with `TolerationSeconds == nil` (or a larger value) as a superset of one with a shorter `TolerationSeconds`, an attacker-supplied toleration that matches (or blanket-matches via `Operator: Exists`) the namespace's mandated `NoExecute` taint can cause the merge to drop the namespace's short-lived default entirely, leaving only the attacker's unbounded toleration.

### Finding Description
In `Admit`, on pod creation the plugin fetches the namespace default tolerations and merges them with the pod-supplied ones: [1](#0-0) 

`pod.Spec.Tolerations` (fully attacker-controlled) is passed as `first` and the namespace defaults as `second` into `MergeTolerations`: [2](#0-1) 

The redundancy check relies on `isSuperset`, whose `NoExecute`/`TolerationSeconds` handling only restricts the comparison when the candidate superset (`ss`) itself carries a `TolerationSeconds`, and only when `ss.Effect == NoExecute` explicitly: [3](#0-2) 

Consequences:
1. If the attacker submits a toleration matching the same `Key`/`Effect` as the namespace default but with `TolerationSeconds: nil` (or a larger value than the namespace's), that attacker toleration is a superset of the namespace default (`isSuperset(attackerToleration, nsDefault) == true`), so the namespace default is dropped from the merged list and the attacker's unbounded toleration survives — verified by the existing unit test table row `"foo-noexec"` being asserted a superset of `"foo-noexec-10"`/`"foo-noexec-0"`: [4](#0-3) .
2. Even more generally, the attacker doesn't need to know the specific taint key at all: submitting a blanket toleration `{Operator: Exists}` (empty `Key`, empty `Effect`) is a superset of *every* toleration including any `NoExecute` one with `TolerationSeconds` set, because the `ss.Effect == NoExecute` guard is skipped entirely when `ss.Effect == ""`. This is confirmed by the `"all"` test row listing `"foo-noexec-10"`, `"foo-noexec-0"` as subsets: [5](#0-4) .

`Validate` only re-checks the merged tolerations against an optional namespace/cluster *whitelist* annotation (`NSWLTolerations`), a separate, independently-configured control from `NSDefaultTolerations`: [6](#0-5) 

If the namespace admin configured only `NSDefaultTolerations` (a very common setup, since the whitelist is a separate opt-in annotation), there is no check preventing the merged result from containing the attacker's more permissive toleration — the admission chain treats the merge as final and complete, silently swallowing the mandated restriction instead of rejecting or overriding it.

### Impact Explanation
This breaks the security guarantee that `PodTolerationRestriction` + namespace `defaultTolerations` is supposed to provide: mandatory eviction of tenant pods from tainted/isolation-boundary nodes after a bounded `TolerationSeconds`. An unprivileged tenant with only `create pods` in their own namespace can neutralize the eviction-based isolation enforcement, keeping pods scheduled/running on nodes they should be evicted from — a workload/tenant isolation bypass (maps to the Kubernetes bounty "workload isolation escape via admission bypass" class).

### Likelihood Explanation
- Requires only standard, minimal RBAC to create pods in one's own namespace — no elevated permissions.
- The namespace must have `scheduler.alpha.kubernetes.io/defaultTolerations` configured with a `NoExecute` toleration and `TolerationSeconds` set (as stated in the precondition), and must not also configure a matching restrictive `tolerationsWhitelist` (a very plausible/common real-world configuration since the two annotations are independent).
- No specific knowledge of the taint key is even required if the attacker uses a blanket `{Operator: Exists}` toleration; a targeted attack (same key/effect, larger/nil `TolerationSeconds`) is trivial if the key is known or discoverable (e.g., readable namespace annotations, documentation, or common isolation-taint conventions).
- Fully repeatable and deterministic — no race conditions or timing involved.

### Recommendation
Change the merge semantics in the `PodTolerationRestriction` admission path so that namespace/cluster-mandated default tolerations act as an upper bound that pod-supplied tolerations cannot loosen: either merge with `first`/`second` order reversed and prefer-first semantics that pin the namespace-mandated toleration, or explicitly clamp any attacker-provided toleration's `TolerationSeconds` to be no greater than the namespace default's before/after merging (i.e., don't let `isSuperset` allow an unbounded/larger `TolerationSeconds`, or a blanket `Operator: Exists` toleration, to elide a namespace-mandated `NoExecute` restriction). Alternatively, after merging, explicitly re-validate that the namespace-mandated tolerations (by key/effect) are still present in the final list with a `TolerationSeconds` no larger than mandated, failing admission otherwise.

### Proof of Concept
Extend `pkg/util/tolerations/tolerations_test.go`'s `TestMergeTolerations` table with a case using the existing `foo-noexec` / `foo-noexec-10` fixtures, mirroring the admission call order `MergeTolerations(podTolerations, namespaceDefaults)`:
```go
{
    name:     "attacker unbounded overrides namespace-mandated NoExecute default",
    a:        []string{"foo-noexec"},     // attacker pod toleration, TolerationSeconds=nil
    b:        []string{"foo-noexec-10"},  // namespace-mandated default, TolerationSeconds=10
    expected: []string{"foo-noexec"},     // BUG: namespace's restrictive default is dropped
},
```
Also add an admission-level integration test in `plugin/pkg/admission/podtolerationrestriction/admission_test.go`: set namespace annotation `NSDefaultTolerations` to a `NoExecute` toleration with `TolerationSeconds: 10`, submit a `Create` pod with an identical `Key`/`Effect` toleration but `TolerationSeconds: nil` (or `{Operator: Exists}` blanket), call `Admit` then `Validate`, and assert that admission either rejects the pod or that `pod.Spec.Tolerations` still contains a toleration with `TolerationSeconds <= 10` for that key/effect. Currently this assertion fails, demonstrating the bypass.

### Citations

**File:** plugin/pkg/admission/podtolerationrestriction/admission.go (L85-112)
```go
	pod := a.GetObject().(*api.Pod)
	var extraTolerations []api.Toleration
	if a.GetOperation() == admission.Create {
		ts, err := p.getNamespaceDefaultTolerations(a.GetNamespace())
		if err != nil {
			return err
		}

		// If the namespace has not specified its default tolerations,
		// fall back to cluster's default tolerations.
		if ts == nil {
			ts = p.pluginConfig.Default
		}

		extraTolerations = ts
	}

	if qoshelper.GetPodQOS(pod) != api.PodQOSBestEffort {
		extraTolerations = append(extraTolerations, api.Toleration{
			Key:      corev1.TaintNodeMemoryPressure,
			Operator: api.TolerationOpExists,
			Effect:   api.TaintEffectNoSchedule,
		})
	}
	// Final merge of tolerations irrespective of pod type.
	if len(extraTolerations) > 0 {
		pod.Spec.Tolerations = tolerations.MergeTolerations(pod.Spec.Tolerations, extraTolerations)
	}
```

**File:** plugin/pkg/admission/podtolerationrestriction/admission.go (L117-151)
```go
func (p *Plugin) Validate(ctx context.Context, a admission.Attributes, o admission.ObjectInterfaces) error {
	if shouldIgnore(a) {
		return nil
	}

	if !p.WaitForReady() {
		return admission.NewForbidden(a, fmt.Errorf("not yet ready to handle request"))
	}

	// whitelist verification.
	pod := a.GetObject().(*api.Pod)
	if len(pod.Spec.Tolerations) > 0 {
		whitelist, err := p.getNamespaceTolerationsWhitelist(a.GetNamespace())
		whitelistScope := "namespace"
		if err != nil {
			return err
		}

		// If the namespace has not specified its tolerations whitelist,
		// fall back to cluster's whitelist of tolerations.
		if whitelist == nil {
			whitelist = p.pluginConfig.Whitelist
			whitelistScope = "cluster"
		}

		if len(whitelist) > 0 {
			// check if the merged pod tolerations satisfy its namespace whitelist
			if !tolerations.VerifyAgainstWhitelist(pod.Spec.Tolerations, whitelist) {
				return fmt.Errorf("pod tolerations (possibly merged with namespace default tolerations) conflict with its %s whitelist", whitelistScope)
			}
		}
	}

	return nil
}
```

**File:** pkg/util/tolerations/tolerations.go (L47-70)
```go
func MergeTolerations(first, second []api.Toleration) []api.Toleration {
	all := append(first, second...)
	var merged []api.Toleration

next:
	for i, t := range all {
		for _, t2 := range merged {
			if isSuperset(t2, t) {
				continue next // t is redundant; ignore it
			}
		}
		if i+1 < len(all) {
			for _, t2 := range all[i+1:] {
				// If the tolerations are equal, prefer the first.
				if !apiequality.Semantic.DeepEqual(&t, &t2) && isSuperset(t2, t) {
					continue next // t is redundant; ignore it
				}
			}
		}
		merged = append(merged, t)
	}

	return merged
}
```

**File:** pkg/util/tolerations/tolerations.go (L84-96)
```go
	// An empty effect means match all effects.
	if t.Effect != ss.Effect && ss.Effect != "" {
		return false
	}

	if ss.Effect == api.TaintEffectNoExecute {
		if ss.TolerationSeconds != nil {
			if t.TolerationSeconds == nil ||
				*t.TolerationSeconds > *ss.TolerationSeconds {
				return false
			}
		}
	}
```

**File:** pkg/util/tolerations/tolerations_test.go (L126-127)
```go
		"all",
		[]string{"all-nosched", "all-noexec", "foo", "foo-bar", "foo-nosched", "foo-bar-nosched", "foo-baz-nosched", "faz-nosched", "faz-baz-nosched", "foo-prefnosched", "foo-noexec", "foo-bar-noexec", "foo-noexec-10", "foo-noexec-0", "foo-bar-noexec-10"},
```

**File:** pkg/util/tolerations/tolerations_test.go (L156-157)
```go
		"foo-noexec",
		[]string{"foo-noexec", "foo-bar-noexec", "foo-noexec-10", "foo-noexec-0", "foo-bar-noexec-10"},
```
