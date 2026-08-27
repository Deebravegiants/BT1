### Title
Priority admission grants unprivileged pods `system-cluster-critical`/`system-node-critical` scheduling priority regardless of namespace - ([File: plugin/pkg/admission/priority/admission.go])

### Summary
The `Priority` admission plugin (`plugin/pkg/admission/priority/admission.go`, `admitPod`/`establishPriority`) resolves a Pod's `spec.PriorityClassName` against the cluster's `PriorityClass` objects and assigns the corresponding `spec.Priority` value with no check on the requesting namespace or the caller's authorization to "use" that class. Any authenticated user with namespace-scoped `create pods` RBAC can set `PriorityClassName: system-cluster-critical` (or `system-node-critical`) on a Pod in any namespace they control and have it admitted with `Priority = scheduling.SystemCriticalPriority` (2,000,000,000) or higher.

### Finding Description
`admitPod` calls `establishPriority(a, &pod.Spec.PriorityClassName)` on Create, which calls `resolvePriorityClass` to look up the named `PriorityClass` via the lister with no additional authorization or namespace check: [1](#0-0) [2](#0-1) [3](#0-2) 

There is no code path in `admission.go` that inspects `attributes.GetNamespace()` and restricts resolution of `system-*` priority classes to `kube-system` (or any privileged namespace), nor any RBAC-style "use" verb check comparable to what protects other privileged resources (no `priorityclasses` "use" verb rule exists, confirmed by search). The system priority classes (`system-node-critical` at `SystemCriticalPriority+1000`, `system-cluster-critical` at `SystemCriticalPriority`) are auto-bootstrapped cluster-wide objects: [4](#0-3) 
and are readable/resolvable by name from any namespace since `PriorityClass` is a cluster-scoped resource with no per-namespace restriction enforced here.

This matches the repository's own test suite, which explicitly documents and asserts this behavior as the current expected outcome — a pod in a non-system namespace referencing `scheduling.SystemClusterCritical` is admitted without error and granted `scheduling.SystemCriticalPriority`: [5](#0-4) [6](#0-5) 

Historically (per this repo's own changelog for v1.11), the `Priority`/`PodPriority` admission plugin restricted `system-node-critical`/`system-cluster-critical` to the `kube-system` namespace: [7](#0-6) 
but no such check exists in the current `admission.go`, and the current unit test suite treats the unrestricted (cross-namespace) behavior as correct/expected.

### Impact Explanation
A Pod admitted with `SystemCriticalPriority` (2×10^9, higher than any user-definable priority capped at `HighestUserDefinablePriority` = 10^9) will:
- Be exempt from normal preemption and be able to preempt lower-priority pods across the cluster during scheduling (scheduler-level effect, not directly shown here but is the documented purpose of this priority band).
- Bypass resource-quota "critical pods" scoping that is designed to gate this priority band to `kube-system` (see `cluster/gce/addons/admission-resource-quota-critical-pods/resource-quota.yaml`, which assumes the critical-pod priority classes are namespace-scoped to `kube-system`): [8](#0-7) 

This is a control-plane/isolation-boundary violation: an unprivileged tenant claims a protected, system-reserved identity/priority level intended only for cluster-critical system components, matching the "Admission bypass -> control of a protected field/identity" impact class.

### Likelihood Explanation
- Minimal precondition: RBAC permission to `create` Pods in any namespace the attacker controls (a very common, low-privilege capability).
- No feature gate guards this — `admitPod`'s Create path is unconditional.
- Fully deterministic and repeatable: any Pod spec with `priorityClassName: system-cluster-critical` will be admitted with the elevated priority, as confirmed by the existing table-driven test case "pod with system critical priority in non-system namespace".
- The `PriorityClass` objects `system-node-critical`/`system-cluster-critical` are always present (auto-created via `AddSystemPriorityClasses` `PostStartHook`), so the attacker does not need to create them: [9](#0-8) 

### Recommendation
Reintroduce a namespace (or authorization) check in `admitPod`/`establishPriority` in `plugin/pkg/admission/priority/admission.go` so that resolution of any `PriorityClass` whose name has the `system-` prefix (or whose `Value` >= `scheduling.HighestUserDefinablePriority`) is rejected unless the Pod's namespace is `kube-system` (or the requesting user/service account is authorized via a SubjectAccessReview "use" check against that specific `PriorityClass`, similar to PodSecurity/PSP "use" semantics). Reject with `admission.NewForbidden` otherwise.

### Proof of Concept
Add/extend `TestPodAdmission` in `plugin/pkg/admission/priority/admission_test.go`:
1. Register the existing `systemClusterCritical` PriorityClass in the fake lister.
2. Submit a Pod Create request with `Namespace: "non-system-namespace"` and `Spec.PriorityClassName: scheduling.SystemClusterCritical` (this is exactly `pods[7]` / the existing test case at lines 483-497 and 680-687).
3. Assert `Admit()` returns a **forbidden error** (post-fix expectation) instead of the current behavior where `expectError = false` and `expectedPriority = scheduling.SystemCriticalPriority` is silently assigned.
4. Additionally assert that the same Pod submitted with `Namespace: metav1.NamespaceSystem` (kube-system) is still admitted successfully with `SystemCriticalPriority`, preserving legitimate system component functionality.

### Citations

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

**File:** plugin/pkg/admission/priority/admission.go (L313-327)
```go
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

**File:** pkg/apis/scheduling/v1/helpers.go (L26-44)
```go
// SystemPriorityClasses define system priority classes that are auto-created at cluster bootstrapping.
// Our API validation logic ensures that any priority class that has a system prefix or its value
// is higher than HighestUserDefinablePriority is equal to one of these SystemPriorityClasses.
var systemPriorityClasses = []*v1.PriorityClass{
	{
		ObjectMeta: metav1.ObjectMeta{
			Name: scheduling.SystemNodeCritical,
		},
		Value:       scheduling.SystemCriticalPriority + 1000,
		Description: "Used for system critical pods that must not be moved from their current node.",
	},
	{
		ObjectMeta: metav1.ObjectMeta{
			Name: scheduling.SystemClusterCritical,
		},
		Value:       scheduling.SystemCriticalPriority,
		Description: "Used for system critical pods that must run in the cluster, but can be moved to another node if necessary.",
	},
}
```

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

**File:** CHANGELOG/CHANGELOG-1.11.md (L930-930)
```markdown
* The `system-node-critical` and `system-cluster-critical` priority classes are now limited to the `kube-system` namespace by the `PodPriority` admission plugin. ([#65593](https://github.com/kubernetes/kubernetes/pull/65593), [@bsalamat](https://github.com/bsalamat))
```

**File:** cluster/gce/addons/admission-resource-quota-critical-pods/resource-quota.yaml (L1-18)
```yaml
# critical pods are configured as a limited resource by admission_controller_config.yaml,
# which means they are disallowed unless explicitly allowed by a namespaced quota object.
# This quota effectively removes the restriction on the number of critical pods allowed in the kube-system namespace.
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gcp-critical-pods
  namespace: kube-system
  labels:
    addonmanager.kubernetes.io/mode: Reconcile
spec:
  hard:
    pods: "1000000000"
  scopeSelector:
    matchExpressions:
    - operator : In
      scopeName: PriorityClass
      values: ["system-node-critical", "system-cluster-critical"]
```

**File:** pkg/registry/scheduling/rest/storage_scheduling.go (L172-207)
```go
func AddSystemPriorityClasses() genericapiserver.PostStartHookFunc {
	return func(hookContext genericapiserver.PostStartHookContext) error {
		// Adding system priority classes is important. If they fail to add, many critical system
		// components may fail and cluster may break.
		err := wait.Poll(1*time.Second, 30*time.Second, func() (done bool, err error) {
			schedClientSet, err := schedulingclient.NewForConfig(hookContext.LoopbackClientConfig)
			if err != nil {
				utilruntime.HandleError(fmt.Errorf("unable to initialize client: %v", err))
				return false, nil
			}

			for _, pc := range schedulingapiv1.SystemPriorityClasses() {
				_, err := schedClientSet.PriorityClasses().Get(context.TODO(), pc.Name, metav1.GetOptions{})
				if err != nil {
					if apierrors.IsNotFound(err) {
						_, err := schedClientSet.PriorityClasses().Create(context.TODO(), pc, metav1.CreateOptions{})
						if err == nil || apierrors.IsAlreadyExists(err) {
							klog.Infof("created PriorityClass %s with value %v", pc.Name, pc.Value)
							continue
						}
						// ServiceUnavailble error is returned when the API server is blocked by storage version updates
						if apierrors.IsServiceUnavailable(err) {
							klog.Infof("going to retry, unable to create PriorityClass %s: %v", pc.Name, err)
							return false, nil
						}
						return false, err
					} else {
						// Unable to get the priority class for reasons other than "not found".
						klog.Warningf("unable to get PriorityClass %v: %v. Retrying...", pc.Name, err)
						return false, nil
					}
				}
			}
			klog.Infof("all system priority classes are created successfully or already exist.")
			return true, nil
		})
```
