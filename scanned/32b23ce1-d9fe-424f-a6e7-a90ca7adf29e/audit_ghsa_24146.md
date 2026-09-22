# [M] github.com/gofiber/fiber/v2 vulnerable to Origin Validation Error

## Summary
Severity: Medium
Advisory: GHSA-927h-x4qj-r242
CVE: CVE-2018-20744
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-927h-x4qj-r242
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v2` — affected >=2.0.0 <2.43.0
- Go: `github.com/rs/cors` — affected >=0 <1.5.0

## Details
The Olivier Poitrey Go CORS handler through 1.3.0 actively converts a wildcard CORS policy into reflecting an arbitrary Origin header value, which is incompatible with the CORS security design, and could lead to CORS misconfiguration security problems.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20744
- https://github.com/gofiber/fiber/issues/2338
- https://github.com/rs/cors/issues/55
- https://github.com/gofiber/fiber/pull/2339
- https://github.com/rs/cors/pull/57
- https://github.com/gofiber/fiber
- https://web.archive.org/web/20200227091122/http://www.securityfocus.com/bid/106834
- https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-chen.pdf
