# [M] CVE-2026-26379

## Summary
Severity: Medium
Advisory: CVE-2026-26379
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-26379
Type: osv

## Details
Koha versions up to 25.11 contain a Server-Side Request Forgery (SSRF) vulnerability via the Z39.50/SRU server configuration. This allows authenticated attackers to perform internal network scanning and identify running services by analyzing server response times.

## References
- https://g03m0n.github.io/
- https://g03m0n.github.io/posts/cve-2026-26379/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26379.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26379
- https://github.com/Koha-Community/Koha
