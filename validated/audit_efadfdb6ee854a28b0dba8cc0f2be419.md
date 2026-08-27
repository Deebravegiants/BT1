This confirms the finding: the test explicitly asserts `expectError == false` for `"pod with system critical priority in non-system namespace"`, i.e. `pods[7]` (namespace `"non-system-namespace"`, `PriorityClassName: scheduling.SystemClusterCritical`) is expected to succeed and resolve to `scheduling.SystemCriticalPriority`, confirming there is no namespace-scoped or RBAC-scoped restriction currently enforced in `admitPod` for system-prefixed PriorityClasses. [1](#0-0) [2](#0-1) 

### Title
Unprivileged users can assign system-critical PriorityClasses to Pods with no authorization or namespace check - ([File: plugin/pkg/admission/priority/admission.go])

### Summary
`Plugin.admitPod` resolves `spec.PriorityClassName` purely by name lookup via `establishPriority`/`resolvePriorityClass`, with no authorizer call and no check that the referenced PriorityClass is a system-reserved class the caller/namespace is entitled to use. Any user who can create Pods can set `priorityClassName: system-cluster-critical` (or `system-node-critical`) in any namespace and have `pod.Spec.Priority` set to `scheduling.SystemCriticalPriority`, with no `Forbidden` error.

### Finding Description
`admitPod` on `admission.Create` calls `p.establishPriority(a, &pod.Spec.PriorityClassName)`, which calls `p.resolvePriorityClass(attributes, *priorityClassName)`; this only does `p.lister.Get(priorityClassName)` — a pure object lookup with no `Attributes`-based authorization decision and no check of `attributes.GetNamespace()` against `metav1.NamespaceSystem`, nor any RBAC/SubjectAccessReview against the `priorityclasses` resource. [3](#0-2) [4](#0-3) [5](#0-4) 

The CHANGELOG for v1.11 documents that this restriction was originally intended: "The `system-node-critical` and `system-cluster-critical` priority classes are now limited to the `kube-system` namespace by the `PodPriority` admission plugin" — but no such enforcement exists anywhere in this admission plugin's current code (`Admit`, `admitPod`, `establishPriority`, `resolvePriorityClass`), and the plugin's own test suite explicitly asserts that a pod in `"non-system-namespace"` using `scheduling.SystemClusterCritical` succeeds with `expectError: false` and priority resolved to `scheduling.SystemCriticalPriority`. [2](#0-1) [1](#0-0) 

`ValidatePriorityClass` (used only when creating/updating a `PriorityClass` object, gated by RBAC on `priorityclasses`) restricts who may *create* a class named with the `system-` prefix, but says nothing about who may *reference* an existing class by name on a Pod. [6](#0-5) 

Attacker flow: with only `create` RBAC on `pods` (no rights on `priorityclasses`), POST a Pod with `spec.priorityClassName: "system-cluster-critical"`; admission mutates `pod.Spec.Priority` to `scheduling.SystemCriticalPriority` and does not reject the request, because no authorizer/binding check ties usage of a PriorityClass to the caller's RBAC.

### Impact Explanation
This is a privilege-escalation / authorization-bypass class issue: an unprivileged Pod-creator can force scheduler-level system-critical priority and preemption semantics (system-critical Pods can preempt virtually anything and are protected from eviction/OOM in ways ordinary pods are not), letting a low-privilege tenant disrupt cluster-wide scheduling and resource guarantees intended to be reserved for control-plane components in `kube-system`. This corresponds to the Kubernetes bug-bounty "privilege escalation via admission bypass" impact class.

### Likelihood Explanation
Minimal precondition: RBAC `create` on `pods` in any namespace, no `priorityclasses` permissions required. The exploit is a single Pod Create call with a known well-formed field and is fully repeatable/deterministic since PriorityClass resolution is a pure name lookup with no caller-context check.

### Recommendation
Reinstate an authorization/scoping check in `admitPod`/`establishPriority`/`resolvePriorityClass`: either (a) restrict usage of system-prefixed PriorityClasses (`system-node-critical`, `system-cluster-critical`) to Pods in `kube-system` (per historical behavior), and/or (b) require the caller to have explicit RBAC `use` verb on the referenced `priorityclasses` resource (mirroring how `PodSecurityPolicy`/`ValidatingAdmissionPolicy` "use" bindings gate privileged object references), returning `admission.NewForbidden` otherwise.

### Proof of Concept
Table-driven test (extending existing `TestPodAdmission` in `plugin/pkg/admission/priority/admission_test.go`):
1. Create a `Pod` in namespace `"non-system-namespace"` (or any non-`kube-system` namespace) with `Spec.PriorityClassName = scheduling.SystemClusterCritical`.
2. Register `systemClusterCritical` PriorityClass in the lister.
3. Call `p.Admit(...)` (Create operation) via the plugin's `Admit`/`admitPod`.
4. Assert `err == nil` (no `Forbidden` error is returned) and `*pod.Spec.Priority == scheduling.SystemCriticalPriority`.
5. Confirm `grep`/trace shows no `authorizer.Authorize` or `SubjectAccessReview` call anywhere in `admitPod`, `establishPriority`, or `resolvePriorityClass`.

This matches the existing test case `"pod with system critical priority in non-system namespace"` at [1](#0-0)  which already demonstrates `expectError: false`.

### Citations

**File:** plugin/pkg/admission/priority/admission_test.go (L483-497)
```go
		// pod[7]: Pod with a system priority class name in non-system namespace
		{
			ObjectMeta: metav1.ObjectMeta{
				Name:      "pod-w-system-priority-in-nonsystem-namespace",
				Namespace: "non-system-namespace",
			},
			Spec: api.PodSpec{
				Containers: []api.Container{
					{
						Name: containerName,
					},
				},
				PriorityClassName: scheduling.SystemClusterCritical,
			},
		},
```

**File:** plugin/pkg/admission/priority/admission_test.go (L680-687)
```go
		{
			"pod with system critical priority in non-system namespace",
			[]*scheduling.PriorityClass{systemClusterCritical},
			*pods[7],
			scheduling.SystemCriticalPriority,
			false,
			nil,
		},
```

**File:** plugin/pkg/admission/priority/admission.go (L175-187)
```go
	if operation == admission.Create {
		var priority int32
		var preemptionPolicy *apiv1.PreemptionPolicy
		pcName, priority, preemptionPolicy, err := p.establishPriority(a, &pod.Spec.PriorityClassName)
		if err != nil {
			return err
		}
		pod.Spec.PriorityClassName = pcName
		// if the pod contained a priority that differs from the one computed from the priority class, error
		if pod.Spec.Priority != nil && *pod.Spec.Priority != priority {
			return admission.NewForbidden(a, fmt.Errorf("the integer value of priority (%d) must not be provided in pod spec; priority admission controller computed %d from the given PriorityClass name", *pod.Spec.Priority, priority))
		}
		pod.Spec.Priority = &priority
```

**File:** plugin/pkg/admission/priority/admission.go (L307-327)
```go
// establishPriority is an auxiliary method for calculating the priority-specific fields
// based on the provided priority class name.
// If the provided name is empty, we fall back to getting the default priority class and
// returning information contained there.
// If the provided name is not empty, we get the priority class with such name and return
// the information contained in that class.
func (p *Plugin) establishPriority(attributes admission.Attributes, priorityClassName *string) (string, int32, *apiv1.PreemptionPolicy, error) {
	if priorityClassName == nil || *priorityClassName == "" {
		pcName, priority, preemptionPolicy, err := p.getDefaultPriority()
		if err != nil {
			return "", 0, nil, fmt.Errorf("error occurred while retrieving default priority class: %w", err)
		}
		return pcName, priority, preemptionPolicy, nil
	}
	// Try resolving the priority class name.
	pc, err := p.resolvePriorityClass(attributes, *priorityClassName)
	if err != nil {
		return "", 0, nil, err
	}
	return *priorityClassName, pc.Value, pc.PreemptionPolicy, nil
}
```

**File:** plugin/pkg/admission/priority/admission.go (L359-368)
```go
func (p *Plugin) resolvePriorityClass(attributes admission.Attributes, priorityClassName string) (*schedulingv1.PriorityClass, error) {
	priorityClass, err := p.lister.Get(priorityClassName)
	if err != nil {
		if errors.IsNotFound(err) {
			return nil, admission.NewForbidden(attributes, fmt.Errorf("no PriorityClass with name %v was found", priorityClassName))
		}
		return nil, fmt.Errorf("failed to resolve PriorityClass with name %s: %w", priorityClassName, err)
	}
	return priorityClass, nil
}
```

**File:** pkg/apis/scheduling/validation/validation.go (L43-55)
```go
func ValidatePriorityClass(pc *scheduling.PriorityClass) field.ErrorList {
	allErrs := field.ErrorList{}
	allErrs = append(allErrs, apivalidation.ValidateObjectMeta(&pc.ObjectMeta, false, apimachineryvalidation.NameIsDNSSubdomain, field.NewPath("metadata"))...)
	// If the priorityClass starts with a system prefix, it must be one of the
	// predefined system priority classes.
	if strings.HasPrefix(pc.Name, scheduling.SystemPriorityClassPrefix) {
		if is, err := schedulingapiv1.IsKnownSystemPriorityClass(pc.Name, pc.Value, pc.GlobalDefault); !is {
			allErrs = append(allErrs, field.Forbidden(field.NewPath("metadata", "name"), "priority class names with '"+scheduling.SystemPriorityClassPrefix+"' prefix are reserved for system use only. error: "+err.Error()))
		}
	} else if pc.Value > scheduling.HighestUserDefinablePriority {
		// Non-system critical priority classes are not allowed to have a value larger than HighestUserDefinablePriority.
		allErrs = append(allErrs, field.Forbidden(field.NewPath("value"), fmt.Sprintf("maximum allowed value of a user defined priority is %v", scheduling.HighestUserDefinablePriority)))
	}
```
