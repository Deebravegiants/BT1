# [M] CVE-2024-28565

## Summary
Severity: Medium
Advisory: CVE-2024-28565
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-28565
Type: osv

## Details
Buffer Overflow vulnerability in open source FreeImage v.3.19.0 [r1909] allows a local attacker to cause a denial of service (DoS) via the psdParser::ReadImageData() function when reading images in PSD format.

## References
- http://www.openwall.com/lists/oss-security/2024/04/11/10
- http://www.openwall.com/lists/oss-security/2024/04/11/2
- http://www.openwall.com/lists/oss-security/2024/04/11/3
- https://github.com/Ruanxingzhi/vul-report/tree/master/freeimage-r1909
