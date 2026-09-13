# [H] CVE-2021-32142

## Summary
Severity: High
Advisory: CVE-2021-32142
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-02-17
Source: https://osv.dev/vulnerability/CVE-2021-32142
Type: osv

## Details
Buffer Overflow vulnerability in LibRaw linux/unix v0.20.0 allows attacker to escalate privileges via the LibRaw_buffer_datastream::gets(char*, int) in /src/libraw/src/libraw_datastream.cpp.

## References
- https://github.com/gtt1995
- https://lists.debian.org/debian-lts-announce/2023/05/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5ICTVDRGBWGIFBTUWJLGX7QM5GWBWUG7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E7TEZ7CLRNYYQZJ5NJGZXK6YJU46WH2L/
- https://www.libraw.org/
- https://www.debian.org/security/2023/dsa-5412
- https://github.com/LibRaw/LibRaw/issues/400
- https://github.com/LibRaw/LibRaw/commit/bc3aaf4223fdb70d52d470dae65c5a7923ea2a49
