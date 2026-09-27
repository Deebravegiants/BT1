# [C] Kanboard is Vulnerable to Reverse Proxy Authentication Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-21881
Aliases: GHSA-wwpf-3j4p-739w
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-21881
Type: osv

## Details
Kanboard is project management software focused on Kanban methodology. Versions 1.2.48 and below is vulnerable to a critical authentication bypass when REVERSE_PROXY_AUTH is enabled. The application blindly trusts HTTP headers for user authentication without verifying the request originated from a trusted reverse proxy. An attacker can impersonate any user, including administrators, by simply sending a spoofed HTTP header. This issue is fixed in version 1.2.49.

## References
- https://github.com/kanboard/kanboard/releases/tag/v1.2.49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21881.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-wwpf-3j4p-739w
- https://nvd.nist.gov/vuln/detail/CVE-2026-21881
- https://github.com/kanboard/kanboard/commit/7af6143e2ad25b5c15549cca8af4341c7ac4e2fc
