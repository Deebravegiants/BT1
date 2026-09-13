# [M] Apache CloudStack: Domain/account resources limits not honored

## Summary
Severity: Medium
Advisory: CVE-2025-69233
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2025-69233
Type: osv

## Details
Due to multiple time-of-check time-of-use race conditions in the resource count check and increment logic, as well as missing validations, users of the platform are able to exceed the allocation limits configured for their accounts/domains. This can be used by an attacker to degrade the infrastructure's resources and lead to denial of service conditions.

Users are recommended to upgrade to Apache CloudStack versions 4.20.3.0 or 4.22.0.1, or later, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/09/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69233.json
- https://lists.apache.org/thread/n8mt5b7wkpysstb8w7rr9f02kc5cq2xm
- https://nvd.nist.gov/vuln/detail/CVE-2025-69233
