# [M] Apache CloudStack: DoS caused by database connections leak

## Summary
Severity: Medium
Advisory: CVE-2026-59654
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-59654
Type: osv

## Details
Missing Release of Resource after Effective Lifetime vulnerability in Apache CloudStack's scoped global configuration functionality. It affects different modules and plugins of the CloudStack management server, including Quota, Host-HA, etc., and may lead to eventual denial of service (DoS) scenario for the management server.

This issue affects Apache CloudStack: from 4.7.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.

Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59654.json
- https://lists.apache.org/thread/7cgf37clcpjj4g2hl7rnyoq1th3ht9r4
- https://nvd.nist.gov/vuln/detail/CVE-2026-59654
