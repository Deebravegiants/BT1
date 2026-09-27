# [H] Improper Parameter Check in ThreadX Syscall Implementation

## Summary
Severity: High
Advisory: CVE-2025-55080
Aliases: GHSA-76hh-wrj5-hr2v
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-55080
Type: osv

## Details
In Eclipse ThreadX before 6.4.3, when memory protection is enabled, syscall parameters verification wasn't enough, allowing an attacker to obtain an arbitrary memory read/write.

## References
- https://github.com/eclipse-threadx/threadx/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55080.json
- https://github.com/eclipse-threadx/threadx/security/advisories/GHSA-76hh-wrj5-hr2v
- https://nvd.nist.gov/vuln/detail/CVE-2025-55080
