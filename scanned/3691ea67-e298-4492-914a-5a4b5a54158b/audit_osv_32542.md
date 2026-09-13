# [M] CVE-2025-32359

## Summary
Severity: Medium
Advisory: CVE-2025-32359
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-04-05
Source: https://osv.dev/vulnerability/CVE-2025-32359
Type: osv

## Details
In Zammad 6.4.x before 6.4.2, there is client-side enforcement of server-side security. When changing their two factor authentication configuration, users need to re-authenticate with their current password first. However, this change was enforced in Zammad only on the front end level, and not when using the API directly.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32359.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32359
- https://zammad.com/en/advisories/zaa-2025-02
