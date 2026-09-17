# [C] Traefik affected by Go HTTP Request Smuggling Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5423-jcjm-2gpv
CWE: CWE-1395
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-04-18
Source: https://github.com/advisories/GHSA-5423-jcjm-2gpv
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.24
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.3.6
- Go: `github.com/traefik/traefik/v3` — affected >=3.4.0-rc1 <3.4.0-rc2

## Details
### Summary
net/http: request smuggling through invalid chunked data: The net/http package accepts data in the chunked transfer encoding containing an invalid chunk-size line terminated by a bare LF. When used in conjunction with a server or proxy which incorrectly interprets a bare LF in a chunk extension as part of the extension, this could permit request smuggling. [CVE-2025-22871] Vendor Affected Components: Go: 1.23.x < 1.23.8

More Details: [CVE-2025-22871](https://nvd.nist.gov/vuln/detail/CVE-2025-22871)

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.24
- https://github.com/traefik/traefik/releases/tag/v3.3.6
- https://github.com/traefik/traefik/releases/tag/v3.4.0-rc2

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-5423-jcjm-2gpv
- https://nvd.nist.gov/vuln/detail/CVE-2025-22871
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.24
- https://github.com/traefik/traefik/releases/tag/v3.3.6
- https://github.com/traefik/traefik/releases/tag/v3.4.0-rc2
