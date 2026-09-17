# [H] CVE-2024-25269

## Summary
Severity: High
Advisory: CVE-2024-25269
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-05
Source: https://osv.dev/vulnerability/CVE-2024-25269
Type: osv

## Details
libheif <= 1.17.6 contains a memory leak in the function JpegEncoder::Encode. This flaw allows an attacker to cause a denial of service attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25269.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25269
- https://github.com/strukturag/libheif/issues/1073
