# [M] iTop dashboard vulnerable to denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-24785
Aliases: GHSA-49rq-cgv9-7hv4
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-24785
Type: osv

## Details
iTop is an web based IT Service Management tool. In version 3.2.0, an attacker may send a URL to the server to trigger a PHP error. The next user trying to load this dashboard would encounter a crashed start page. Version 3.2.1 fixes the issue by checking the provided layout_class before saving the dashboard.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24785.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-49rq-cgv9-7hv4
- https://nvd.nist.gov/vuln/detail/CVE-2025-24785
