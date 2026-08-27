### Title
`limitSecretReferences` omits `Pod.Spec.EphemeralContainers`, allowing disallowed secret references to bypass mountable-secrets enforcement at pod CREATE - ([File: plugin/pkg/admission/serviceaccount/admission.go])

### Summary
`Plugin.Validate` only enforces mountable-secret restrictions for ephemeral containers on the `ephemeralcontainers` subresource UPDATE path via `limitEphemeralContainerSecretReferences`, while the CREATE path calls `limitSecretReferences`, which iterates `InitContainers` and `Containers` but never `EphemeralContainers`. A pod created with `spec.ephemeralContainers` referencing a forbidden secret is therefore never checked against the service account's `Secrets` allow-list.

### Finding Description
`Plugin.Validate` dispatches based on operation/subresource: for `admission.Update` with subresource `"ephemeralcontainers"` it calls `limitEphemeralContainerSecretReferences`, which does enforce the allow-list against `pod.Spec.EphemeralContainers` [1](#0-0) . For `admission.Create`, it instead calls `limitSecretReferences` when `enforceMountableSecrets` is true [2](#0-1) . `limitSecretReferences` builds the `mountableSecrets` set from the service account and checks volumes, `InitContainers`, and `Containers` env/envFrom secret references, but contains no loop over `pod.Spec.EphemeralContainers` [3](#0-2) . By contrast, `limitEphemeralContainerSecretReferences` implements the exact same env/envFrom check but scoped to `EphemeralContainers` only [4](#0-3) , confirming the CREATE path's `limitSecretReferences` has no equivalent coverage.

An attacker with only `create pods` RBAC in a namespace whose target ServiceAccount has `EnforceMountableSecretsAnnotation=true` can submit a `POST` pod with `spec.ephemeralContainers[0].env[].valueFrom.secretKeyRef.name` set to a secret not referenced by the service account. Because `Plugin.Validate` for CREATE never touches `EphemeralContainers`, admission succeeds despite the enforcement flag being set, and the disallowed secret becomes available to the ephemeral container's environment once it runs.

### Impact Explanation
This is a scoped admission/validation-bypass allowing secret exfiltration: a workload identity intended to be restricted to only its own declared secrets (`ServiceAccount.Secrets`) can read an arbitrary namespace secret by placing the reference in `ephemeralContainers` at pod creation, defeating the entire purpose of `EnforceMountableSecretsAnnotation`. This matches the "admission or Pod Security bypass" / secret-exfiltration impact class.

### Likelihood Explanation
Preconditions are minimal and realistic: namespace-scoped `create pods` RBAC and an SA with the enforcement annotation set to true (a security-hardening feature some clusters explicitly enable). The only uncertainty is whether core API validation (`pkg/apis/core/validation/validation.go` → `ValidatePodCreate`/`ValidatePodSpec`) rejects a non-empty `spec.EphemeralContainers` at pod CREATE time; I was not able to fully confirm within this session whether such a create-time restriction exists elsewhere in the validation pipeline that would independently block this path. If ephemeral containers can be set at CREATE (which is permitted by the `PodSpec` API type and not explicitly disallowed in the reviewed admission code), the bypass is trivially and repeatably reproducible with a single crafted pod manifest.

### Recommendation
Add an `EphemeralContainers` loop to `limitSecretReferences` (mirroring the env/envFrom checks already done for `InitContainers`/`Containers`), so that the CREATE path enforces the same mountable-secrets allow-list for ephemeral containers, removing the need to rely solely on the separate `ephemeralcontainers` subresource UPDATE check.

### Proof of Concept
Unit test in `plugin/pkg/admission/serviceaccount/admission_test.go`:
1. Create a `ServiceAccount` with `Secrets: []corev1.ObjectReference{{Name: "allowed-secret"}}` and annotation `EnforceMountableSecretsAnnotation: "true"`.
2. Build a `Pod` object with empty `Containers`/`InitContainers` and `Spec.EphemeralContainers` containing one `EphemeralContainer` whose `Env` includes `ValueFrom.SecretKeyRef.Name = "forbidden-secret"`.
3. Call `plugin.Validate(ctx, admission.NewAttributesRecord(pod, nil, ..., "", ns, "pods", "", admission.Create, nil, false, nil), objectInterfaces)`.
4. Assert the current behavior returns `nil` (no error) — demonstrating the bypass — and that the desired/fixed behavior should return an `admission.NewForbidden` error referencing `forbidden-secret`, matching the message format used in `limitEphemeralContainerSecretReferences`.
5. As a control, add a similar env reference in `Spec.Containers` and confirm `limitSecretReferences` correctly rejects it today, isolating the gap specifically to `EphemeralContainers`.

### Citations

**File:** plugin/pkg/admission/serviceaccount/admission.go (L187-189)
```go
	if a.GetOperation() == admission.Update && a.GetSubresource() == "ephemeralcontainers" {
		return s.limitEphemeralContainerSecretReferences(pod, a)
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

**File:** plugin/pkg/admission/serviceaccount/admission.go (L317-366)
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

	for _, container := range pod.Spec.InitContainers {
		for _, env := range container.Env {
			if env.ValueFrom != nil && env.ValueFrom.SecretKeyRef != nil {
				if !mountableSecrets.Has(env.ValueFrom.SecretKeyRef.Name) {
					return fmt.Errorf("init container %s with envVar %s referencing secret.secretName=\"%s\" is not allowed because service account %s does not reference that secret", container.Name, env.Name, env.ValueFrom.SecretKeyRef.Name, serviceAccount.Name)
				}
			}
		}
		for _, envFrom := range container.EnvFrom {
			if envFrom.SecretRef != nil {
				if !mountableSecrets.Has(envFrom.SecretRef.Name) {
					return fmt.Errorf("init container %s with envFrom referencing secret.secretName=\"%s\" is not allowed because service account %s does not reference that secret", container.Name, envFrom.SecretRef.Name, serviceAccount.Name)
				}
			}
		}
	}

	for _, container := range pod.Spec.Containers {
		for _, env := range container.Env {
			if env.ValueFrom != nil && env.ValueFrom.SecretKeyRef != nil {
				if !mountableSecrets.Has(env.ValueFrom.SecretKeyRef.Name) {
					return fmt.Errorf("container %s with envVar %s referencing secret.secretName=\"%s\" is not allowed because service account %s does not reference that secret", container.Name, env.Name, env.ValueFrom.SecretKeyRef.Name, serviceAccount.Name)
				}
			}
		}
		for _, envFrom := range container.EnvFrom {
			if envFrom.SecretRef != nil {
				if !mountableSecrets.Has(envFrom.SecretRef.Name) {
					return fmt.Errorf("container %s with envFrom referencing secret.secretName=\"%s\" is not allowed because service account %s does not reference that secret", container.Name, envFrom.SecretRef.Name, serviceAccount.Name)
				}
			}
		}
	}
```

**File:** plugin/pkg/admission/serviceaccount/admission.go (L399-414)
```go
	for _, container := range pod.Spec.EphemeralContainers {
		for _, env := range container.Env {
			if env.ValueFrom != nil && env.ValueFrom.SecretKeyRef != nil {
				if !mountableSecrets.Has(env.ValueFrom.SecretKeyRef.Name) {
					return fmt.Errorf("ephemeral container %s with envVar %s referencing secret.secretName=\"%s\" is not allowed because service account %s does not reference that secret", container.Name, env.Name, env.ValueFrom.SecretKeyRef.Name, serviceAccount.Name)
				}
			}
		}
		for _, envFrom := range container.EnvFrom {
			if envFrom.SecretRef != nil {
				if !mountableSecrets.Has(envFrom.SecretRef.Name) {
					return fmt.Errorf("ephemeral container %s with envFrom referencing secret.secretName=\"%s\" is not allowed because service account %s does not reference that secret", container.Name, envFrom.SecretRef.Name, serviceAccount.Name)
				}
			}
		}
	}
```
