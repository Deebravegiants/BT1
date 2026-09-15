# [C] CVE-2022-38143

## Summary
Severity: Critical
Advisory: CVE-2022-38143
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-38143
Type: osv

## Details
A heap out-of-bounds write vulnerability exists in the way OpenImageIO v2.3.19.0 processes RLE encoded BMP images. A specially-crafted bmp file can write to arbitrary out of bounds memory, which can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1630
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/38xxx/CVE-2022-38143.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-38143
- https://security.gentoo.org/glsa/202305-33
