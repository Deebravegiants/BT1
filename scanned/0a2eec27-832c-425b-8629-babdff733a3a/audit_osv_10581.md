# [C] CVE-2017-17480

## Summary
Severity: Critical
Advisory: CVE-2017-17480
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-08
Source: https://osv.dev/vulnerability/CVE-2017-17480
Type: osv

## Details
In OpenJPEG 2.3.0, a stack-based buffer overflow was discovered in the pgxtovolume function in jp3d/convert.c. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service or possibly remote code execution.

## References
- https://github.com/uclouvain/openjpeg/issues/1044
- https://lists.debian.org/debian-lts-announce/2018/11/msg00018.html
- https://usn.ubuntu.com/4109-1/
- https://www.debian.org/security/2019/dsa-4405
