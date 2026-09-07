# [H] nebula-mesh: GET /api/v1/audit-log discloses all entries to any operator

## Summary
Severity: High
Advisory: GHSA-qm33-p5p9-f8vg
CVE: CVE-2026-47726
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-qm33-p5p9-f8vg
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.2

## Details
`internal/api/audit.go:12` — `handleGetAuditLog` does no admin check. The route is bearer-auth gated only; any operator API key returns the full audit log via `store.ListAuditEntries` (up to limit=1000). This includes cross-tenant actor names, host/CA/operator IDs, action timestamps, and masked-IP entries from rate-limit refusals — enough surface for a tenant to enumerate the server's activity, infer staffing patterns, or identify high-value targets.

## Affected
All released versions up to v0.3.1.

## Reproducer
```
curl -H "Authorization: Bearer <any-operator-key>" \
  https://server/api/v1/audit-log?limit=1000
```

## Suggested fix
Two options, either acceptable:

1. `if !actorIsAdmin(ctx) { 403 }` — strictest; matches the "operator management is admin-only" stance.
2. Scope to actor: filter `store.ListAuditEntries` by `actor.Username` plus a subquery of CA IDs the actor owns. Operators see their own audit entries plus entries against their CA's resources.

Recommend option 1 unless the UI needs per-operator audit views.

## Suggested patch

Verified locally: `go vet`, `go test -race -count=1 ./...`, `golangci-lint v2.12` all clean.

```diff
diff --git a/internal/api/audit.go b/internal/api/audit.go
index 3236631..57b57ce 100644
--- a/internal/api/audit.go
+++ b/internal/api/audit.go
@@ -10,6 +10,10 @@ import (
 const defaultAuditLimit = 100
 
 func (s *Server) handleGetAuditLog(w http.ResponseWriter, r *http.Request) {
+	if !actorIsAdmin(r.Context()) {
+		writeError(w, http.StatusForbidden, "audit log access requires the admin role")
+		return
+	}
 	filter := store.AuditFilter{
 		Action: r.URL.Query().Get("action"),
 		Limit:  defaultAuditLimit,
diff --git a/internal/api/audit_admin_test.go b/internal/api/audit_admin_test.go
new file mode 100644
index 0000000..47e1ca4
--- /dev/null
+++ b/internal/api/audit_admin_test.go
@@ -0,0 +1,62 @@
+package api
+
+import (
+	"context"
+	"crypto/sha256"
+	"encoding/hex"
+	"net/http"
+	"net/http/httptest"
+	"testing"
+
+	"github.com/google/uuid"
+	"github.com/juev/nebula-mesh/internal/models"
+)
+
+// TestHandleGetAuditLog_NonAdminForbidden confirms a non-admin operator
+// API key cannot read the audit log. The legacy config-key path stays
+// admin and is covered by the happy-path test elsewhere.
+func TestHandleGetAuditLog_NonAdminForbidden(t *testing.T) {
+	srv, _ := newTestServer(t)
+
+	nonAdminKey := uuid.New().String()
+	keyHash := sha256.Sum256([]byte(nonAdminKey))
+	if err := srv.store.CreateOperator(context.Background(), &models.Operator{
+		ID: uuid.New().String(), Username: "non-admin", PasswordHash: "x",
+		Role: "user", Status: models.OperatorStatusActive,
+	}); err != nil {
+		t.Fatal(err)
+	}
+	op, err := srv.store.GetOperatorByUsername(context.Background(), "non-admin")
+	if err != nil {
+		t.Fatal(err)
+	}
+	if err := srv.store.CreateOperatorAPIKey(context.Background(), &models.OperatorAPIKey{
+		ID: uuid.New().String(), OperatorID: op.ID, KeyHash: hex.EncodeToString(keyHash[:]),
+	}); err != nil {
+		t.Fatal(err)
+	}
+
+	req := httptest.NewRequest("GET", "/api/v1/audit-log", nil)
+	req.Header.Set("Authorization", "Bearer "+nonAdminKey)
+	rec := httptest.NewRecorder()
+	srv.ServeHTTP(rec, req)
+
+	if rec.Code != http.StatusForbidden {
+		t.Errorf("non-admin audit-log status = %d, want 403", rec.Code)
+	}
+}
+
+// TestHandleGetAuditLog_LegacyKeyAllowed confirms the legacy config-key
+// path still reaches the handler (preserves backward compatibility).
+func TestHandleGetAuditLog_LegacyKeyAllowed(t *testing.T) {
+	srv, _ := newTestServer(t)
+
+	req := httptest.NewRequest("GET", "/api/v1/audit-log", nil)
+	req.Header.Set("Authorization", "Bearer "+testAPIKey)
+	rec := httptest.NewRecorder()
+	srv.ServeHTTP(rec, req)
+
+	if rec.Code == http.StatusForbidden {
+		t.Errorf("legacy key rejected with 403; want pass-through")
+	}
+}
```

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-qm33-p5p9-f8vg
- https://github.com/forgekeep/nebula-mesh/commit/8baaace54c2a23e7c351b3efab5a31ab07b125dc
- https://github.com/forgekeep/nebula-mesh/releases/tag/v0.3.2
- https://github.com/juev/nebula-mesh
