### Title
`limitSecretReferences` fails to validate Secret references inside `Projected` volume sources, allowing cross-tenant secret disclosure - ([File: plugin/pkg/admission/serviceaccount/admission.go])

### Summary
The `ServiceAccount` admission plugin's `limitSecretReferences` function only inspects `volume.VolumeSource.Secret` when enforcing the `enforce-mountable-secrets` restriction, but does not inspect `volume.VolumeSource.Projected.Sources[].Secret`. An unprivileged user who can only create pods in their own namespace, targeting a service account with `kubernetes.io/enforce-mountable-secrets=true`, can mount any secret in the namespace via a `Projected` volume, bypassing the mountable-secrets restriction entirely.

### Finding Description
`Plugin.Validate` calls `s.limitSecretReferences(serviceAccount, pod)` whenever `s.enforceMountableSecrets(serviceAccount)` is true (either via the global `LimitSecretReferences` flag or the per-SA `kubernetes.io/enforce-mountable-secrets` annotation). [1](#0-0) 

Inside `limitSecretReferences`, the volume-scanning loop only unwraps `volume.VolumeSource` and checks `source.Secret`: [2](#0-1) 

It never walks `volume.VolumeSource.Projected.Sources`, unlike the mirror-pod path in `Validate`, which does explicitly walk `v.Projected.Sources` (but only to block `ServiceAccountToken` projections, not to validate `Secret` projections): [3](#0-2) 

Because of this gap, a pod spec such as:
```yaml
volumes:
- name: exfil
  projected:
    sources:
    - secret:
        name: victim-secret   # not in serviceAccount.Secrets
```
passes `limitSecretReferences` unchecked, even though a `volumes[].secret.secretName` reference to the same secret would be rejected. The attacker only needs RBAC to create pods in a namespace using a service account that has the enforce-mountable-secrets annotation, and knowledge (or a guess) of another secret's name in the same namespace.

### Impact Explanation
This allows disclosure of secrets that the pod's service account is not authorized to mount, defeating the purpose of the `enforce-mountable-secrets` control, which is specifically designed to scope which secrets a workload's identity may access. This matches the "unauthorized cross-tenant/cross-identity secret read" impact class — an attacker escalates from "create pods" RBAC to reading arbitrary namespace secrets that were deliberately withheld from their service account.

### Likelihood Explanation
Preconditions are minimal and realistic: RBAC permission to create pods in a namespace, and the target service account has `kubernetes.io/enforce-mountable-secrets: "true"` (a supported, documented hardening mechanism). No special privileges, admission webhook bypass, or node access is required — this is a standard `pods create` request through the public API. The exploit is fully reproducible and deterministic.

### Recommendation
Extend `limitSecretReferences` to also walk `volume.VolumeSource.Projected.Sources` and validate any `Secret` projection's `Name` against `mountableSecrets`, mirroring the pattern already used for the plain `Secret` volume source (and consistent with how `podutil.VisitPodSecretNames` already enumerates projected secret sources elsewhere in the codebase).

### Proof of Concept
Add a table-driven test case to `plugin/pkg/admission/serviceaccount/admission_test.go` (alongside existing `limitSecretReferences`/mountable-secrets tests):
1. Create a `ServiceAccount` with `Secrets: []corev1.ObjectReference{{Name: "allowed-secret"}}` and annotation `kubernetes.io/enforce-mountable-secrets: "true"`.
2. Construct a `Pod` with `Spec.Volumes` containing a `Projected` volume whose `Sources` include `{Secret: &api.SecretProjection{LocalObjectReference: api.LocalObjectReference{Name: "victim-secret"}}}` (not in the SA's `Secrets`).
3. Call `Plugin.Validate` (or `Admit`) with this pod/SA via the admission attributes.
4. Expected (currently failing) assertion: `err` should be a forbidden error (`admission.NewForbidden`) referencing `victim-secret`; currently the call returns `nil`, demonstrating the bypass.

### Citations

**File:** plugin/pkg/admission/serviceaccount/admission.go (L209-217)
```go
		for _, v := range pod.Spec.Volumes {
			if proj := v.Projected; proj != nil {
				for _, projSource := range proj.Sources {
					if projSource.ServiceAccountToken != nil {
						return admission.NewForbidden(a, fmt.Errorf("a mirror pod may not use ServiceAccountToken volume projections"))
					}
				}
			}
		}
```

**File:** plugin/pkg/admission/serviceaccount/admission.go (L231-235)
```go
	if s.enforceMountableSecrets(serviceAccount) {
		if err := s.limitSecretReferences(serviceAccount, pod); err != nil {
			return admission.NewForbidden(a, err)
		}
	}
```

**File:** plugin/pkg/admission/serviceaccount/admission.go (L317-332)
```go
func (s *Plugin) limitSecretReferences(serviceAccount *corev1.ServiceAccount, pod *api.Pod) error {
	// Ensure all secrets the pod references are allowed by the service account
	mountableSecrets := sets.NewString()
	for _, s := range serviceAccount.Secrets {
		mountableSecrets.Insert(s.Name)
	}
	for _, volume := range pod.Spec.Volumes {
		source := volume.VolumeSource
		if source.Secret == nil {
			continue
		}
		secretName := source.Secret.SecretName
		if !mountableSecrets.Has(secretName) {
			return fmt.Errorf("volume with secret.secretName=\"%s\" is not allowed because service account %s does not reference that secret", secretName, serviceAccount.Name)
		}
	}
```
