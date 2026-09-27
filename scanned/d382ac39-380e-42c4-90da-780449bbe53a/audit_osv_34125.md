# [M] Missing check for thread priority

## Summary
Severity: Medium
Advisory: CVE-2025-55079
Aliases: GHSA-w8rw-fqgj-9r49
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-55079
Type: osv

## Details
In Eclipse ThreadX before version 6.4.3, the thread module has a setting of maximum priority. In some cases the check of that maximum priority wasn't performed, allowing, as a result, to obtain a thread with higher priority than expected and causing a possible denial of service.

## References
- https://github.com/eclipse-threadx/threadx/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55079.json
- https://github.com/eclipse-threadx/threadx/security/advisories/GHSA-w8rw-fqgj-9r49
- https://nvd.nist.gov/vuln/detail/CVE-2025-55079
