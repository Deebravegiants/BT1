# [C] CVE-2024-46958

## Summary
Severity: Critical
Advisory: CVE-2024-46958
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-09-16
Source: https://osv.dev/vulnerability/CVE-2024-46958
Type: osv

## Details
In Nextcloud Desktop Client 3.13.1 through 3.13.3 on Linux, synchronized files (between the server and client) may become world writable or world readable. This is fixed in 3.13.4.

## References
- https://github.com/nextcloud/desktop/compare/v3.13.3...v3.13.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46958.json
- https://github.com/nextcloud/security-advisories/security/advisories
- https://nvd.nist.gov/vuln/detail/CVE-2024-46958
- https://github.com/nextcloud/desktop/issues/6863
- https://github.com/nextcloud/desktop/pull/6949
- https://github.com/nextcloud/desktop/pull/7092
