# [H] Traefik HTTP/2 connections management could cause a denial of service

## Summary
Severity: High
Advisory: GHSA-c6hx-pjc3-7fqr
CVE: CVE-2022-39271
CWE: CWE-400, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-10
Source: https://github.com/advisories/GHSA-c6hx-pjc3-7fqr
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.8.8
- Go: `github.com/traefik/traefik/v2` — affected >=2.9.0-rc1 <2.9.0-rc5

## Details
### Impact

There is a potential vulnerability in Traefik managing HTTP/2 connections.
A closing HTTP/2 server connection could hang forever because of a subsequent fatal error. This failure mode could be exploited to cause a denial of service.

### Patches

Traefik v2.8.x: https://github.com/traefik/traefik/releases/tag/v2.8.8
Traefik v2.9.x: https://github.com/traefik/traefik/releases/tag/v2.9.0-rc5

### Workarounds

No workaround.

### For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-c6hx-pjc3-7fqr
- https://nvd.nist.gov/vuln/detail/CVE-2022-39271
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.8.8
- https://github.com/traefik/traefik/releases/tag/v2.9.0-rc5
