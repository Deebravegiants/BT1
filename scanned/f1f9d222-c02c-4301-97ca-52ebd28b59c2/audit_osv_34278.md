# [H] CVE-2025-57403

## Summary
Severity: High
Advisory: CVE-2025-57403
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-26
Source: https://osv.dev/vulnerability/CVE-2025-57403
Type: osv

## Details
Cola Dnslog v1.3.2 is vulnerable to Directory Traversal. When a DNS query for a TXT record is processed, the application concatenates the requested URL (or a portion of it) directly with a base path using os.path.join. This bypass allows directory traversal or absolute path injection, leading to the potential exposure of sensitive information.

## References
- https://gist.github.com/Captaince/99b728c792c72b2666c2400625702df0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57403.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57403
- https://github.com/AbelChe/cola_dnslog/issues/29
