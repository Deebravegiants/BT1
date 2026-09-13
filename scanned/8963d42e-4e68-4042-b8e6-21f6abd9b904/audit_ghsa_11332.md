# [M] Traefik Vulnerable to BasicAuth/DigestAuth Identity Spoofing via Non-Canonical headerField

## Summary
Severity: Medium
Advisory: GHSA-qr99-7898-vr7c
CVE: CVE-2026-33433
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-qr99-7898-vr7c
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.42
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta1 <3.6.12
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-ea.3

## Details
## Summary

There is a potential vulnerability in Traefik's Basic and Digest authentication middlewares when `headerField` is configured with a non-canonical HTTP header name.

An authenticated attacker with valid credentials can inject the canonical version of the configured header to impersonate any identity to the backend. Because Traefik writes the authenticated username using a non-canonical map key, it creates a separate header entry rather than overwriting the attacker's canonical one — causing most backend frameworks to read the attacker-controlled value instead.

## Patches

- <https://github.com/traefik/traefik/releases/tag/v2.11.42>
- <https://github.com/traefik/traefik/releases/tag/v3.6.12>
- <https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.3>

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

---

<details>
<summary>Original Description</summary>

### Summary

When `headerField` is configured with a non-canonical HTTP header name (e.g., `x-auth-user` instead of `X-Auth-User`), an authenticated attacker can inject a canonical version of that header to impersonate any identity to the backend. The backend receives two header entries — the attacker-injected canonical one is read first, overriding Traefik's non-canonical write.

Tested on Traefik v3.6.10.

### Details

At `pkg/middlewares/auth/basic_auth.go:92`, the authenticated username is written using direct map assignment:

```go
req.Header[b.headerField] = []string{user}
```

Go's `http.Header` map is keyed by canonical names (e.g., `X-Auth-User`). Direct assignment with a non-canonical key (`x-auth-user`) creates a separate map entry from any canonical-key entry already present. The attacker's `X-Auth-User: superadmin` occupies the canonical slot and is never overwritten by Traefik's non-canonical write.

The same bug exists in `pkg/middlewares/auth/digest_auth.go:100`. Notably, `forward.go:254` correctly uses `http.CanonicalHeaderKey()`, showing the fix pattern already exists in the codebase.

### PoC

**Traefik config (YAML, Docker labels, or REST API):**

```yaml
middlewares:
  auth:
    basicAuth:
      users: ["admin:$2y$05$..."]
      headerField: "x-auth-user"
```

**Normal request (baseline):**

```bash
curl -u admin:admin http://traefik/secure/test
# Backend receives: x-auth-user: admin
# Identity = admin ✓
```

**Attack request:**

```bash
curl -u admin:admin -H "X-Auth-User: superadmin" http://traefik/secure/test
# Backend receives BOTH headers:
#   X-Auth-User: superadmin   ← attacker-injected (canonical key, read first by most frameworks)
#   x-auth-user: admin        ← Traefik-set (non-canonical, ignored by most frameworks)
# Identity seen by backend = superadmin ✗
```

**Control test** — when `headerField` uses canonical casing (`X-Auth-User`), the attack fails. Traefik's write correctly overwrites the attacker's header.

This is realistic because YAML conventions favor lowercase keys, Traefik docs don't warn about canonicalization, and the pattern of backends trusting the `headerField` header is recommended in Traefik's own documentation.

**Fix suggestion:**

```go
// basic_auth.go:92 and digest_auth.go:100 — change:
req.Header[b.headerField] = []string{user}
// to:
req.Header.Set(b.headerField, user)
```

Also strip any incoming `headerField` header before the auth check with `req.Header.Del(b.headerField)`.

### Impact

An authenticated attacker with valid credentials (even low-privilege) can impersonate any other user identity to backend services. If backends use the `headerField` header for authorization decisions (which is the intended use case per Traefik docs), this enables privilege escalation — e.g., a regular user impersonating an admin.

The attack requires the operator to configure `headerField` with a non-canonical header name, which is the natural thing to do in YAML and is not warned against in documentation.

</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-qr99-7898-vr7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33433
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.42
- https://github.com/traefik/traefik/releases/tag/v3.6.11
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.3
