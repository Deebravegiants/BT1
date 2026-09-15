# [M] CVE-2019-13147

## Summary
Severity: Medium
Advisory: CVE-2019-13147
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-02
Source: https://osv.dev/vulnerability/CVE-2019-13147
Type: osv

## Details
In Audio File Library (aka audiofile) 0.3.6, there exists one NULL pointer dereference bug in ulaw2linear_buf in G711.cpp in libmodules.a that allows an attacker to cause a denial of service via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/11/msg00006.html
- https://github.com/mpruett/audiofile/issues/54
