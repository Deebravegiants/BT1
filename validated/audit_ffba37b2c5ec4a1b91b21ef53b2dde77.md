### Title
`limitSecretReferences` fails to check Projected volume Secret sources, allowing bypass of LimitSecretReferences secret allowlist - ([File: plugin/pkg/admission/serviceaccount/admission.go])

### Summary
The `limitSecretReferences` function in the ServiceAccount admission plugin only inspects `volume.VolumeSource.Secret` when validating that a pod's mounted secrets are allowlisted by the pod's service account, but never inspects `Projected.Sources[].Secret`. When `LimitSecretReferences` (or the per-SA `EnforceMountableSecretsAnnotation`) is enabled, a pod can reference an arbitrary, non-allowlisted secret via a `Projected` volume and bypass the check entirely.

### Finding Description
`s.Validate` calls `s.limitSecretReferences(serviceAccount, pod)` when `s.enforceMountableSecrets(serviceAccount)` is true [1](#0-0) . Inside `limitSecretReferences`, the volume loop only examines `volume.VolumeSource.Secret` and skips any volume where that field is nil: [2](#0-1) 

There is no equivalent handling for `volume.VolumeSource.Projected.Sources[].Secret`, even though `api.ProjectedVolumeSource` / `VolumeProjection` supports a `Secret` field that mounts an arbitrary named Secret exactly like the direct `Secret` volume source (this is used elsewhere in the same file for legitimate projected sources, e.g. `TokenVolumeSource` builds a `Projected` volume with `ServiceAccountToken`/`ConfigMap`/`DownwardAPI` sources) [3](#0-2) .

An attacker with only namespace-scoped `create pods` RBAC (and no RBAC to `get` the target Secret) can construct a Pod with `spec.volumes[].projected.sources[].secret.name = <victim-secret>`. Because the volume loop in `limitSecretReferences` never inspects `Projected.Sources[].Secret`, the function returns `nil` and the pod is admitted, and the kubelet (using its own elevated node credentials, not the pod's RBAC) fetches and mounts the secret into the pod, exposing its contents to the attacker's container filesystem.

### Impact Explanation
This is a workload-isolation / secret-confinement bypass: it defeats the intended purpose of `LimitSecretReferences`/`enforce-mountable-secrets`, which exists specifically to prevent a pod from mounting secrets that are not explicitly allowlisted on its ServiceAccount. Where this control is relied upon (either via the plugin flag or the per-SA annotation) as a defense against tenants mounting arbitrary secrets in a namespace, an attacker can read any secret in the namespace regardless of the allowlist, purely via the `Projected` volume type — a straightforward `VALIDATION_TOTALITY` gap (incomplete enumeration of equivalent input paths) matching Kubernetes' "unauthorized secret/cross-tenant read" bounty class.

### Likelihood Explanation
Exploitability requires only that the operator has enabled `LimitSecretReferences` (plugin-level) or set `kubernetes.io/enforce-mountable-secrets=true` on the relevant ServiceAccount — both are legitimate, supported administrative configurations of this defense-in-depth control, not attacker-induced misconfigurations. Given that precondition, any user able to create Pods (a minimal, common RBAC grant) can trivially and repeatably construct a `Projected` volume referencing any secret name in the namespace; no other privileges, timing, or race conditions are required. Note that `LimitSecretReferences` defaults to `false` in `NewServiceAccount` [4](#0-3) , so exploitation is only relevant when this legacy control is actively enabled by policy.

### Recommendation
Extend `limitSecretReferences`'s volume loop to also walk `volume.VolumeSource.Projected.Sources` and check any `projSource.Secret.SecretName` against `mountableSecrets`, consistent with how `Validate`'s mirror-pod check already walks `Projected.Sources` for `ServiceAccountToken` [5](#0-4) . Ideally reuse `podutil.VisitPodSecretNames` (which should be verified/extended to cover projected secret sources) rather than a bespoke volume enumeration, to avoid this class of enumeration drift in the future.

### Proof of Concept
Unit test in `plugin/pkg/admission/serviceaccount/admission_test.go` (or new table test):
1. Create a `Plugin` with `LimitSecretReferences = true`.
2. Create a ServiceAccount `sa` in namespace `ns` with `Secrets: []corev1.ObjectReference{{Name: "allowed-secret"}}` (no `"blocked-secret"` reference).
3. Build a Pod with `spec.ServiceAccountName = "sa"` and:
   ```go
   Volumes: []api.Volume{{
       Name: "v",
       VolumeSource: api.VolumeSource{
           Projected: &api.ProjectedVolumeSource{
               Sources: []api.VolumeProjection{{
                   Secret: &api.SecretProjection{
                       LocalObjectReference: api.LocalObjectReference{Name: "blocked-secret"},
                   },
               }},
           },
       },
   }}
   ```
4. Call `plugin.limitSecretReferences(sa, pod)`.
5. Assert the result is `nil` (no error) — proving `blocked-secret` was silently allowed despite not being in the SA's allowlist, whereas an equivalent pod using `VolumeSource.Secret{SecretName: "blocked-secret"}` directly correctly returns a non-nil error.

### Citations

**File:** plugin/pkg/admission/serviceaccount/admission.go (L100-110)
```go
func NewServiceAccount() *Plugin {
	return &Plugin{
		Handler: admission.NewHandler(admission.Create, admission.Update),
		// TODO: enable this once we've swept secret usage to account for adding secret references to service accounts
		LimitSecretReferences: false,
		// Auto mount service account API token secrets
		MountServiceAccountToken: true,

		generateName: names.SimpleNameGenerator.GenerateName,
	}
}
```

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

**File:** plugin/pkg/admission/serviceaccount/admission.go (L487-525)
```go
func TokenVolumeSource() *api.ProjectedVolumeSource {
	return &api.ProjectedVolumeSource{
		// explicitly set default value, see #104464
		DefaultMode: ptr.To[int32](corev1.ProjectedVolumeSourceDefaultMode),
		Sources: []api.VolumeProjection{
			{
				ServiceAccountToken: &api.ServiceAccountTokenProjection{
					Path:              "token",
					ExpirationSeconds: ptr.To[int64](serviceaccount.WarnOnlyBoundTokenExpirationSeconds),
				},
			},
			{
				ConfigMap: &api.ConfigMapProjection{
					LocalObjectReference: api.LocalObjectReference{
						Name: "kube-root-ca.crt",
					},
					Items: []api.KeyToPath{
						{
							Key:  "ca.crt",
							Path: "ca.crt",
						},
					},
				},
			},
			{
				DownwardAPI: &api.DownwardAPIProjection{
					Items: []api.DownwardAPIVolumeFile{
						{
							Path: "namespace",
							FieldRef: &api.ObjectFieldSelector{
								APIVersion: "v1",
								FieldPath:  "metadata.namespace",
							},
						},
					},
				},
			},
		},
	}
```
