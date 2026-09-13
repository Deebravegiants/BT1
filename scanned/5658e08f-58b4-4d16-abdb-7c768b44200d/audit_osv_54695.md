# [M] CVE-2024-28563

## Summary
Severity: Medium
Advisory: CVE-2024-28563
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-28563
Type: osv

## Details
Buffer Overflow vulnerability in open source FreeImage v.3.19.0 [r1909] allows a local attacker to cause a denial of service (DoS) via the Imf_2_2::DwaCompressor::Classifier::Classifier() function when reading images in EXR format.

## References
- http://www.openwall.com/lists/oss-security/2024/04/11/10
- http://www.openwall.com/lists/oss-security/2024/04/11/2
- http://www.openwall.com/lists/oss-security/2024/04/11/3
- https://github.com/Ruanxingzhi/vul-report/tree/master/freeimage-r1909
