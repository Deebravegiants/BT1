# [H] Caido has an insufficient patch for DNS rebind leading to RCE

## Summary
Severity: High
Advisory: CVE-2026-24853
Aliases: GHSA-3q5q-p8vj-8783
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-24853
Type: osv

## Details
Caido is a web security auditing toolkit. Prior to 0.55.0, Caido blocks non whitelisted domains to reach out through the 8080 port, and shows Host/IP is not allowed to connect to Caido on all endpoints. But this is bypassable by injecting a X-Forwarded-Host: 127.0.0.1:8080 header. This vulnerability is fixed in 0.55.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24853.json
- https://github.com/caido/caido/security/advisories/GHSA-3q5q-p8vj-8783
- https://nvd.nist.gov/vuln/detail/CVE-2026-24853
