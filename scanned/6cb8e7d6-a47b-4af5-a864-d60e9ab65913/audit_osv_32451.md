# [M] XMPWorker | Out-of-bounds Read (CWE-125)

## Summary
Severity: Medium
Advisory: CVE-2025-30305
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-30305
Type: osv

## Details
XMP Toolkit versions 2023.12 and earlier are affected by an out-of-bounds read vulnerability that could lead to disclosure of sensitive memory. An attacker could leverage this vulnerability to bypass mitigations such as ASLR. Exploitation of this issue requires user interaction in that a victim must open a malicious file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30305.json
- https://helpx.adobe.com/security/products/xmpcore/apsb25-34.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-30305
