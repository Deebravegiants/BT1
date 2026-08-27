### Title
Owner-reference authorization bypass via duplicate-UID collision in `indexByUID`/`newBlockingOwnerDeletionRefs` - ([File: plugin/pkg/admission/gc/gc_admission.go])

### Summary
`indexByUID` keys prior owner references solely by `UID`, and `ValidateOwnerReferences` never rejects duplicate `UID` values among `ownerReferences`. An attacker can craft two owner references that share the same `UID` but different `Name`/`Kind` — one that they are authorized to make blocking, and one they are not — so the second (unauthorized) reference is later flipped to `blockOwnerDeletion=true` without triggering the delete/finalizer authorization check.

### Finding Description
`ValidateOwnerReferences` in [1](#0-0)  validates each owner reference individually (non-empty `apiVersion`/`kind`/`name`/`uid`, at most one `controller`), but never checks for duplicate `UID` values across the list. So a namespaced user with ordinary create permission on some resource can create it with two owner references sharing one `UID`:

```
refs = [ ownerA{Name:"victim", Kind:"...", UID:X, blockOwnerDeletion:false},
         ownerB{Name:"mine",   Kind:"...", UID:X, blockOwnerDeletion:true} ]
```

Only `ownerB` (`blockOwnerDeletion=true`) is checked at creation, via `newBlockingOwnerDeletionRefs` (oldObj==nil path returns only `blockingNewRefs`) [2](#0-1) , and authorized against `ownerB`'s Name/Kind. `ownerA` requires no permission at all since it is not "blocking".

On a subsequent update, the attacker flips `ownerA.blockOwnerDeletion` to `true` (leaving `ownerB` unchanged). `newBlockingOwnerDeletionRefs` builds `indexedOldRefs := indexByUID(oldMeta.GetOwnerReferences())` [3](#0-2) , which iterates the old refs in order and lets later entries silently overwrite earlier ones sharing the same `UID`. Because `ownerB` (already `blockOwnerDeletion=true`) is the last owner reference with `UID=X`, `indexedOldRefs[X]` resolves to `ownerB`'s old state, not `ownerA`'s.

When the loop then checks the new `ownerA{true}` ref: `oldRef, ok := indexedOldRefs[ref.UID]` returns `ownerB`'s old ref (`BlockOwnerDeletion=true`), so `wasNotBlocking` is `false`, and `ownerA` is treated as "already blocking" and is *not* added to `ret` [4](#0-3) . Consequently `newBlockingRefs` for this update never includes `ownerA`, `Validate` sees `len(newBlockingRefs)==0` and returns `nil` (allowed) [5](#0-4)  without ever calling `ownerRefToDeleteAttributeRecords`/`Authorize` for `ownerA`. The authorization check for setting `blockOwnerDeletion=true` on `ownerA` — which is keyed by `ref.APIVersion`/`ref.Kind`/`ref.Name`, not `UID` [6](#0-5)  — is completely bypassed, even though `ownerA` is a distinct named resource the attacker may have no delete/finalizer permission on.

### Impact Explanation
This breaks the "authorization exactness" guarantee of the `OwnerReferencesPermissionEnforcement` admission plugin: `blockOwnerDeletion=true` is meant to require delete/finalizer permission on the referenced owner (because it can prevent garbage collection/deletion of that owner until the dependent's finalizer clears). The bypass lets an attacker with only namespace-scoped create/update rights on their own dependent resource set a foreground-blocking owner reference to an arbitrary named resource they do not control, interfering with that resource's deletion lifecycle without proving authorization — a control-plane authorization-bypass / privilege-escalation-adjacent issue (unauthorized cross-tenant interference with an unrelated object's deletion).

### Likelihood Explanation
Requires only: (1) permission to create/update an object with `ownerReferences` in the attacker's own namespace (minimal RBAC most tenants have), and (2) delete/finalizer permission on at least one arbitrary resource to seed the colliding blocking reference (`ownerB`) — which can be any resource the attacker legitimately owns. No cluster-admin, webhook, or node access is needed, and the sequence (create then update) is fully repeatable and deterministic once the ordering of the duplicate-UID entries is controlled by the attacker.

### Recommendation
Reject duplicate `UID` values across `ownerReferences` in `ValidateOwnerReferences`, and/or change `indexByUID` / `newBlockingOwnerDeletionRefs` to index by a composite key (`UID` + `APIVersion` + `Kind` + `Name`) instead of `UID` alone, so distinct references cannot collide and mask each other's authorization state.

### Proof of Concept
Add a table test for `newBlockingOwnerDeletionRefs` in `plugin/pkg/admission/gc/gc_admission_test.go`:
- `oldObj`: ownerReferences = `[{Name:"victim",Kind:"Foo",UID:"X",BlockOwnerDeletion:false}, {Name:"mine",Kind:"Foo",UID:"X",BlockOwnerDeletion:true}]`.
- `newObj`: same list except `victim`'s `BlockOwnerDeletion` flipped to `true`.
- Call `newBlockingOwnerDeletionRefs(newObj, oldObj)`.
- Expected (correct) result: the returned slice should contain the `victim` reference (since its blocking state newly changed from false→true) so it gets authorized.
- Actual (buggy) result: the returned slice is empty (`len == 0`), proving the `victim` reference's new blocking flag is never surfaced for authorization — confirming the bypass.

### Citations

**File:** staging/src/k8s.io/apimachinery/pkg/api/validation/objectmeta.go (L97-114)
```go
// ValidateOwnerReferences validates that a set of owner references are correctly defined.
func ValidateOwnerReferences(ownerReferences []metav1.OwnerReference, fldPath *field.Path) field.ErrorList {
	allErrs := field.ErrorList{}
	firstControllerName := ""
	for idx, ref := range ownerReferences {
		allErrs = append(allErrs, validateOwnerReference(ref, fldPath.Index(idx))...)
		if ref.Controller != nil && *ref.Controller {
			curControllerName := ref.Kind + "/" + ref.Name
			if firstControllerName != "" {
				allErrs = append(allErrs, field.Invalid(fldPath, ownerReferences,
					fmt.Sprintf("Only one reference can have Controller set to true. Found \"true\" in references for %v and %v", firstControllerName, curControllerName)))
			} else {
				firstControllerName = curControllerName
			}
		}
	}
	return allErrs
}
```

**File:** plugin/pkg/admission/gc/gc_admission.go (L125-128)
```go
	newBlockingRefs := newBlockingOwnerDeletionRefs(attributes.GetObject(), attributes.GetOldObject())
	if len(newBlockingRefs) == 0 {
		return nil
	}
```

**File:** plugin/pkg/admission/gc/gc_admission.go (L206-235)
```go
func (a *gcPermissionsEnforcement) ownerRefToDeleteAttributeRecords(ref metav1.OwnerReference, attributes admission.Attributes) ([]authorizer.AttributesRecord, error) {
	var ret []authorizer.AttributesRecord
	groupVersion, err := schema.ParseGroupVersion(ref.APIVersion)
	if err != nil {
		return ret, err
	}
	mappings, err := a.restMapper.RESTMappings(schema.GroupKind{Group: groupVersion.Group, Kind: ref.Kind}, groupVersion.Version)
	if err != nil {
		return ret, err
	}
	for _, mapping := range mappings {
		ar := authorizer.AttributesRecord{
			User:            attributes.GetUserInfo(),
			Verb:            "update",
			APIGroup:        mapping.Resource.Group,
			APIVersion:      mapping.Resource.Version,
			Resource:        mapping.Resource.Resource,
			Subresource:     "finalizers",
			Name:            ref.Name,
			ResourceRequest: true,
			Path:            "",
		}
		if mapping.Scope.Name() == meta.RESTScopeNameNamespace {
			// if the owner is namespaced, it must be in the same namespace as the dependent is.
			ar.Namespace = attributes.GetNamespace()
		}
		ret = append(ret, ar)
	}
	return ret, nil
}
```

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

**File:** plugin/pkg/admission/gc/gc_admission.go (L256-272)
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
```

**File:** plugin/pkg/admission/gc/gc_admission.go (L279-293)
```go
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
```
