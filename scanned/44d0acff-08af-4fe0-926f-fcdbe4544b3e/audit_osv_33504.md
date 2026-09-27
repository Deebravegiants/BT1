# [H] Buffer Overflow in Eclipse OpenJ9

## Summary
Severity: High
Advisory: CVE-2025-4447
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:H/SC:H/SI:N/SA:N)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-4447
Type: osv

## Details
In Eclipse OpenJ9 versions up to 0.51, when used with OpenJDK version 8 a stack based buffer overflow can be caused by modifying a file on disk that is read when the JVM starts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4447.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4447
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/61
- https://github.com/eclipse-openj9/openj9/pull/21762
