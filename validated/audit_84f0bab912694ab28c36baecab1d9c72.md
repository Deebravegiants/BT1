### Title
`newBlockingOwnerDeletionRefs`/`indexByUID` UID-collapsing lets an attacker escalate an unrelated ownerReference to `blockOwnerDeletion=true` without the finalizers authorization check - ([File: plugin/pkg/admission/gc/gc_admission.go])

### Summary
`indexByUID` builds a `map[types.UID]metav1.OwnerReference` keyed only on `ref.UID`, discarding `Kind`/`APIVersion`/`Name`. `newBlockingOwnerDeletionRefs` uses this map to decide whether a blocking ownerReference in the new object is "already blocking" in the old object and therefore skip the per-owner authorization check. Because the match is on UID alone, an attacker can keep the UID of a ref they were legitimately allowed to make blocking, while swapping its `Kind`/`Name` to point at a completely different object, causing the plugin to treat the swapped reference as already-authorized and skip the finalizers `Authorize` call in `plugin/pkg/admission/gc/gc_admission.go`.

### Finding Description
The admission flow in `Validate` (`plugin/pkg/admission/gc/gc_admission.go:89-156`) only requires the finalizers/delete authorization check for owner references that `newBlockingOwnerDeletionRefs` reports as newly blocking: [1](#0-0) 

`indexByUID` collapses `oldMeta.GetOwnerReferences()` into a map keyed purely by `UID`: [2](#0-1) 

Exploit flow (unprivileged attacker, namespace-scoped RBAC on their own resource X and a Pod they own):
1. Attacker creates resource X with `ownerReferences: [{UID: <real UID of their own Pod P>, Kind: Pod, Name: P, blockOwnerDeletion: true}]`. Since operation is Create, `newBlockingOwnerDeletionRefs` returns this ref directly (no old refs), and the finalizers check runs against Pod P, which the attacker legitimately controls — authorized and allowed.
2. Attacker updates X, changing the single ownerReference's `Kind`/`APIVersion`/`Name` to point at an unrelated object the attacker does **not** control (e.g., a `kube-system` Secret or a ServiceAccount-owned object), while **keeping the same UID value** (`<real UID of Pod P>`) and `blockOwnerDeletion: true`.
3. `isChangingOwnerReference` (line 158) correctly detects the change (Kind/Name differ) so admission proceeds.
4. The "can you delete the dependent" check (lines 103-120) is on resource X itself, which the attacker owns — passes trivially.
5. `newBlockingOwnerDeletionRefs` computes `indexedOldRefs[UID] = {Kind: Pod, blockOwnerDeletion: true}`. For the new ref (`Kind: Secret`, same UID), `oldRef, ok := indexedOldRefs[ref.UID]` succeeds (`ok=true`) and `wasNotBlocking = false` because the old (Pod) ref was already blocking. The ref is therefore **not** added to `ret`, even though it now points to a completely different object.
6. Because the ref is excluded from `newBlockingRefs`, the loop at lines 138-152 never calls `ownerRefToDeleteAttributeRecords`/`Authorize` for the Secret, so the plugin never checks whether the attacker can set finalizers on the Secret.
7. Result: attacker's object X ends up with `blockOwnerDeletion: true` referencing a resource they have no delete/finalizers permission on, entirely bypassing the intended authorization gate (`AUTHORIZATION_EXACTNESS` violation).

### Impact Explanation
This is an authorization bypass in a control-plane admission plugin (`OwnerReferencesPermissionEnforcement`). The `blockOwnerDeletion` finalizer-style protection is meant to require that only entities who can manage an owner's finalizers may make a dependent block that owner's deletion (this protects against deletion-blocking DoS and to prevent low-privileged users from unexpectedly obstructing deletion of resources they don't control, potentially including sensitive resources such as ServiceAccounts, Secrets, or Namespaces). By forging the UID to alias an unrelated, previously-authorized reference, an unprivileged/namespace-scoped attacker can attach an unauthorized blocking ownerReference to an arbitrary resource, causing deletion of that resource to be blocked by garbage collection without ever passing the intended finalizers authorization check. This is a persisted-invalid-field / authorization-bypass class issue matching "authorizer bypass" / "persisted invalid or protected field" bounty categories.

### Likelihood Explanation
Exploitation only requires standard namespace-scoped RBAC to create/update a single resource with owner references (e.g., `create`/`update` on any resource type, which is extremely common for regular workloads) plus ownership of one throwaway object (e.g., a Pod) whose UID can legitimately be referenced with `blockOwnerDeletion: true`. No cluster-admin, node, or controller privileges are needed. The attack is fully client-side (two API calls: create then update) and deterministically reproducible, since `indexByUID`'s map collapse is a pure function of the request bodies.

### Recommendation
Change `indexByUID` (and the comparison logic in `newBlockingOwnerDeletionRefs`) to match owner references by full identity (`UID` **and** `APIVersion`/`Kind`/`Name`), not by `UID` alone, or key the map by UID but explicitly verify `Kind`/`APIVersion`/`Name` equality before treating an old ref's `blockOwnerDeletion` state as authoritative for a new ref with the same UID. If any of those fields differ, the reference must be treated as a distinct/newly-blocking reference requiring authorization.

### Proof of Concept
Unit/table test in `plugin/pkg/admission/gc/gc_admission_test.go` (or new test):
1. Build `oldObj` with `OwnerReferences: [{UID: "uid-1", Kind: "Pod", Name: "p1", BlockOwnerDeletion: pointer(true)}]`.
2. Build `newObj` with `OwnerReferences: [{UID: "uid-1", Kind: "Secret", Name: "s1", BlockOwnerDeletion: pointer(true)}]`.
3. Call `newBlockingOwnerDeletionRefs(newObj, oldObj)` and assert the returned slice is **non-empty** and contains the Secret ref (expected/fixed behavior) — currently it will return an **empty slice**, proving the bypass.
4. Additionally, a full admission-level test: construct `attributes` for an Update where `authorizer` denies finalizers permission on `Secret/s1` but allows it on `Pod/p1`; call `gcPermissionsEnforcement.Validate`; assert it currently returns `nil` (allowed) instead of `admission.NewForbidden`, demonstrating the authorization bypass end-to-end.

### Citations

**File:** plugin/pkg/admission/gc/gc_admission.go (L248-254)
```go
func indexByUID(refs []metav1.OwnerReference) map[types.UID]metav1.OwnerReference {
	ret := make(map[types.UID]metav1.OwnerReference)
	for _, ref := range refs {
		ret[ref.UID] = ref
	}
	return ret
}
```

**File:** plugin/pkg/admission/gc/gc_admission.go (L256-294)
```go
// Returns new blocking ownerReferences, and references whose blockOwnerDeletion
// field is changed from nil or false to true.
func newBlockingOwnerDeletionRefs(newObj, oldObj runtime.Object) []metav1.OwnerReference {
	newMeta, err := meta.Accessor(newObj)
	if err != nil {
		// if we don't have objectmeta, we don't have the object reference
		return nil
	}
	newRefs := newMeta.GetOwnerReferences()
	blockingNewRefs := blockingOwnerRefs(newRefs)
	if len(blockingNewRefs) == 0 {
		return nil
	}

	if oldObj == nil {
		return blockingNewRefs
	}
	oldMeta, err := meta.Accessor(oldObj)
	if err != nil {
		// if we don't have objectmeta, treat it as if all the ownerReference are newly created
		return blockingNewRefs
	}

	var ret []metav1.OwnerReference
	indexedOldRefs := indexByUID(oldMeta.GetOwnerReferences())
	for _, ref := range blockingNewRefs {
		oldRef, ok := indexedOldRefs[ref.UID]
		if !ok {
			// if ref is newly added, and it's blocking, then returns it.
			ret = append(ret, ref)
			continue
		}
		wasNotBlocking := oldRef.BlockOwnerDeletion == nil || *oldRef.BlockOwnerDeletion == false
		if wasNotBlocking {
			ret = append(ret, ref)
		}
	}
	return ret
}
```
