# [M] Improper File Permission Handling in Google gVisor runsc

## Summary
Severity: Medium
Advisory: CVE-2025-2713
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2025-03-28
Source: https://osv.dev/vulnerability/CVE-2025-2713
Type: osv

## Details
Google gVisor's runsc component exhibited a local privilege escalation vulnerability due to incorrect handling of file access permissions, which allowed unprivileged users to access restricted files. This occurred because the process initially ran with root-like permissions until the first fork.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2713.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2713
- https://github.com/google/gvisor/commit/586c38d70081b13b2ed494cef48e99b93956843e
- https://github.com/google/gvisor
