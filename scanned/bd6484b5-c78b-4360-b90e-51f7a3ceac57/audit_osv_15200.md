# [M] CVE-2019-14442

## Summary
Severity: Medium
Advisory: CVE-2019-14442
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-14442
Type: osv

## Details
In mpc8_read_header in libavformat/mpc8.c in Libav 12.3, an input file can result in an avio_seek infinite loop and hang, with 100% CPU consumption. Attackers could leverage this vulnerability to cause a denial of service via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00000.html
- https://bugzilla.libav.org/show_bug.cgi?id=1159
