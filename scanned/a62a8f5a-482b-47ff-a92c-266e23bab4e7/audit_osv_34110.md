# [M] Vision UI security-kit.js: Potential Uncontrolled Resource Allocation Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-54884
Aliases: GHSA-gg28-wc2c-jjj3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-54884
Type: osv

## Details
Vision UI is a collection of enterprise-grade, dependency-free modules for modern web projects. In versions 1.4.0 and below, the generateSecureId and getSecureRandomInt functions in security-kit versions prior to 3.5.0 (packaged in Vision UI 1.4.0 and below) are vulnerable to Denial of Service (DoS) attacks. The generateSecureId(length) function directly used the length parameter to size a Uint8Array buffer, allowing attackers to exhaust server memory through repeated requests for large IDs since the previous 1024 limit was insufficient. The getSecureRandomInt(min, max) function calculated buffer size based on the range between min and max, where large ranges caused excessive memory allocation and CPU-intensive rejection-sampling loops that could hang the thread. This issue is fixed in version 1.5.0.

## References
- https://github.com/DavidOsipov/Vision-ui/releases/tag/1.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54884.json
- https://github.com/DavidOsipov/Vision-ui/security/advisories/GHSA-gg28-wc2c-jjj3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54884
- https://github.com/DavidOsipov/Vision-ui/commit/74802cd688b661a35e638fc96938d65ca7c05ff5
