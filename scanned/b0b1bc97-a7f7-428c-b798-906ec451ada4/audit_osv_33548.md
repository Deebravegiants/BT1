# [M] USD File Parsing Memory Allocation Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-4605
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2025-06-11
Source: https://osv.dev/vulnerability/CVE-2025-4605
Type: osv

## Details
A maliciously crafted .usdc file, when loaded through Autodesk Maya, can force an uncontrolled memory allocation vulnerability. A malicious actor may leverage this vulnerability to cause a denial-of-service (DoS), or cause data corruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4605.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4605
- https://www.autodesk.com/trust/security-advisories/adsk-sa-2025-0011
- https://github.com/Autodesk/3dsmax-usd
- https://github.com/Autodesk/maya-usd
- https://www.autodesk.com/products/autodesk-access/overview
