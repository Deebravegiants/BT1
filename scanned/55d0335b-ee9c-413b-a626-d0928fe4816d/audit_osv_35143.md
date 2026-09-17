# [C] Apache Uniffle: Insecure SSL Configuration in Uniffle HTTP Client

## Summary
Severity: Critical
Advisory: CVE-2025-68637
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2025-68637
Type: osv

## Details
The Uniffle HTTP client is configured to trust all SSL certificates and

disables hostname verification by default. This insecure configuration
exposes all REST API communication between the Uniffle CLI/client and the
Uniffle Coordinator service to potential Man-in-the-Middle (MITM) attacks.


This issue affects all versions from before 0.10.0.

Users are recommended to upgrade to version 0.10.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/12/27/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68637.json
- https://lists.apache.org/thread/trvdd11hmpbjno3t8rc9okr4t036ox2v
- https://nvd.nist.gov/vuln/detail/CVE-2025-68637
