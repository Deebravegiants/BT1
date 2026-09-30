# [H] 3scale-porta: readonly fields not validated server-side

## Summary
Severity: High
Advisory: CVE-2024-12125
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-11-06
Source: https://osv.dev/vulnerability/CVE-2024-12125
Type: osv

## Details
A flaw was found in the 3scale Developer Portal. When creating or updating an account in the Developer Portal UI it is possible to modify fields explicitly configured as read-only or hidden, allowing an attacker to modify restricted information.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/3scale/porta/
- https://access.redhat.com/security/cve/CVE-2024-12125
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12125.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12125
- https://bugzilla.redhat.com/show_bug.cgi?id=2330214
