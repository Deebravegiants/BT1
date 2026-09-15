# [M] CVE-2018-9132

## Summary
Severity: Medium
Advisory: CVE-2018-9132
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-30
Source: https://osv.dev/vulnerability/CVE-2018-9132
Type: osv

## Details
libming 0.4.8 has a NULL pointer dereference in the getInt function of the decompile.c file. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted swf file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/47KZ5RYWQMBN5DVDITBVRDNDCSFNBJ3V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CQNIJH5EQV2D6KEFGY2467ZS4I7TZLXP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LBFCINUX3XXAPPH77OH6NKACBPFBQXXW/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00017.html
- https://github.com/libming/libming/issues/133
