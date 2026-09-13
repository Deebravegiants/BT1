# [H] CVE-2016-8332

## Summary
Severity: High
Advisory: CVE-2016-8332
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-10-28
Source: https://osv.dev/vulnerability/CVE-2016-8332
Type: osv

## Details
A buffer overflow in OpenJPEG 2.1.1 causes arbitrary code execution when parsing a crafted image. An exploitable code execution vulnerability exists in the jpeg2000 image file format parser as implemented in the OpenJpeg library. A specially crafted jpeg2000 file can cause an out of bound heap write resulting in heap corruption leading to arbitrary code execution. For a successful attack, the target user needs to open a malicious jpeg2000 file. The jpeg2000 image file format is mostly used for embedding images inside PDF documents and the OpenJpeg library is used by a number of popular PDF renderers making PDF documents a likely attack vector.

## References
- http://www.securityfocus.com/bid/93242
- http://www.securitytracker.com/id/1038623
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.debian.org/security/2017/dsa-3768
- https://github.com/uclouvain/openjpeg/releases/tag/v2.1.2
- http://www.talosintelligence.com/reports/TALOS-2016-0193/
