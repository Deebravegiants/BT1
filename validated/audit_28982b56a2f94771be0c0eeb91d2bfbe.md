### Title
`Plugin.limitSecretReferences` fails to validate Projected-volume Secret sources, bypassing service-account mountable-secrets enforcement - ([File: plugin/pkg/admission/serviceaccount/admission.go])

### Summary
`Plugin.limitSecretReferences` only inspects `volume.VolumeSource.Secret` when enforcing that pods may only mount secrets referenced by their service account. It never inspects `volume.VolumeSource.Projected.Sources[].Secret`, so a pod using a `Projected` volume with a `Secret` projection bypasses the `LimitSecretReferences`/`EnforceMountableSecretsAnnotation` enforcement entirely.

### Finding Description
`Plugin.Validate` calls `s.limitSecretReferences(serviceAccount, pod)` when `enforceMountableSecrets` is true (via `LimitSecretReferences` plugin setting or the `EnforceMountableSecretsAnnotation` on the pod's service account) [1](#0-0) . Inside `limitSecretReferences`, only `volume.VolumeSource.Secret` is checked against the set of secrets referenced by the service account: [2](#0-1) 

There is no branch for `volume.VolumeSource.Projected`, whose `Sources` slice (`api.VolumeProjection`) can itself contain a `Secret` projection (`VolumeProjection.Secret *SecretProjection`) referencing an arbitrary secret name in the same namespace. Because this code path is skipped for `Projected` sources, an attacker whose service account is restricted to a limited set of secrets can still mount any secret in the namespace by wrapping the `SecretVolumeSource` in a `Projected` volume instead of a plain `Secret` volume. Notably, `podutil.VisitPodSecretNames` (used elsewhere in this same file for the mirror-pod check) does walk `Projected` sources' `Secret` field, showing the omission in `limitSecretReferences` is inconsistent with the rest of the codebase and not an intentional restriction. The exploitation request is a normal `POST` pod create with `Volumes[].Projected.Sources[].Secret.Name` set to a secret name outside `serviceAccount.Secrets`; no other admission check re-validates this reference, so the pod is admitted and kubelet subsequently mounts the unauthorized secret into the pod's filesystem.

### Impact Explanation
This allows a namespace-scoped, unprivileged principal (that can create pods with any service account they can `use`, and where that service account has `LimitSecretReferences`/`EnforceMountableSecretsAnnotation` restrictions) to read the contents of any Secret in the same namespace that they are not authorized to reference, by mounting it via a Projected volume. This is a cross-tenant/cross-workload secret disclosure within a namespace, undermining the mountable-secrets isolation feature that this admission plugin exists to enforce — matching the "sensitive data disclosure"/"privilege escalation via admission bypass" bounty class.

### Likelihood Explanation
Preconditions: attacker can create Pods (standard `pods` create verb) using a service account that has `LimitSecretReferences` enabled globally, or has the `kubernetes.io/enforce-mountable-secrets: "true"` annotation set on its own service account. This is a common hardening configuration in multi-tenant clusters. Exploitation requires only a single pod-create request with a `Projected` volume — no special RBAC or additional access is needed beyond baseline pod-create permission, making this easily repeatable and low-effort.

### Recommendation
Extend `limitSecretReferences` to also walk `volume.VolumeSource.Projected.Sources` and validate `projSource.Secret.Name` against `mountableSecrets`, mirroring the traversal already performed by `podutil.VisitPodSecretNames`. Ideally, refactor `limitSecretReferences` to reuse `podutil.VisitPodSecretNames` (extended for volumes) or a shared secret-name-visiting helper.

### Proof of Concept
Unit test in `plugin/pkg/admission/serviceaccount/admission_test.go` (or a new table-driven test):
1. Create a `ServiceAccount` object with `Secrets: [{Name: "allowed-secret"}]`.
2. Build a `Pod` with `Spec.ServiceAccountName` set to this SA, and `Spec.Volumes` containing:
   ```go
   {
     Name: "projected-vol",
     VolumeSource: api.VolumeSource{
       Projected: &api.ProjectedVolumeSource{
         Sources: []api.VolumeProjection{
           {Secret: &api.SecretProjection{LocalObjectReference: api.LocalObjectReference{Name: "unauthorized-secret"}}},
         },
       },
     },
   }
   ```
3. Set plugin's `LimitSecretReferences = true` (or set `EnforceMountableSecretsAnnotation` on the SA).
4. Call `Plugin.Validate` (or `Admit`) with a Create admission attribute for this pod.
5. **Expected (secure) result**: `admission.NewForbidden` error referencing `unauthorized-secret`.
6. **Actual (vulnerable) result**: `Validate` returns `nil` (no error), confirming the pod is admitted despite referencing a secret not in `serviceAccount.Secrets`, demonstrating the bypass.

### Citations

**File:** plugin/pkg/admission/serviceaccount/admission.go (L231-235)
```go
	if s.enforceMountableSecrets(serviceAccount) {
		if err := s.limitSecretReferences(serviceAccount, pod); err != nil {
			return admission.NewForbidden(a, err)
		}
	}
```

**File:** plugin/pkg/admission/serviceaccount/admission.go (L323-332)
```go
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
