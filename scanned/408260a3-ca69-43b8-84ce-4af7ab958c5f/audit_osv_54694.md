# [M] CVE-2024-28562

## Summary
Severity: Medium
Advisory: CVE-2024-28562
CVSS: 6.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-28562
Type: osv

## Details
Buffer Overflow vulnerability in open source FreeImage v.3.19.0 [r1909] allows a local attacker to execute arbitrary code via the Imf_2_2::copyIntoFrameBuffer() component when reading images in EXR format.

## References
- http://www.openwall.com/lists/oss-security/2024/04/11/10
- http://www.openwall.com/lists/oss-security/2024/04/11/2
- http://www.openwall.com/lists/oss-security/2024/04/11/3
- https://github.com/Ruanxingzhi/vul-report/tree/master/freeimage-r1909
