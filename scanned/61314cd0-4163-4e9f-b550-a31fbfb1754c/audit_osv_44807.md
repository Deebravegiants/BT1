# [M] knowns before 0.30.0 Path Traversal via templateFile parameter

## Summary
Severity: Medium
Advisory: CVE-2026-86538
Aliases: GHSA-fpxv-c555-rhm3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86538
Type: osv

## Details
knowns versions before 0.30.0 contain a path traversal vulnerability in the POST /api/templates/preview endpoint that allows unauthenticated attackers to read arbitrary files. Attackers can supply directory traversal sequences in the templateFile parameter to bypass path restrictions and read sensitive files like credentials and configuration through the JSON response.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86538.json
- https://github.com/knowns-dev/knowns/releases/tag/v0.30.0
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-fpxv-c555-rhm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-86538
- https://www.vulncheck.com/advisories/knowns-before-0.30.0-path-traversal-via-templatefile-parameter
- https://github.com/knowns-dev/knowns/commit/09c5a96fd5817b941dc86669278c1a17db10ed4e
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/server/routes/templates.go#L299-L310
