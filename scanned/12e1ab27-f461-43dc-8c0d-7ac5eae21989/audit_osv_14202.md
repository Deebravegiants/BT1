# [M] CVE-2018-7873

## Summary
Severity: Medium
Advisory: CVE-2018-7873
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-08
Source: https://osv.dev/vulnerability/CVE-2018-7873
Type: osv

## Details
There is a heap-based buffer overflow in the getString function of util/decompile.c in libming 0.4.8 for INTEGER data. A Crafted input will lead to a denial of service attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/47KZ5RYWQMBN5DVDITBVRDNDCSFNBJ3V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CQNIJH5EQV2D6KEFGY2467ZS4I7TZLXP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LBFCINUX3XXAPPH77OH6NKACBPFBQXXW/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00017.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=892260
- https://github.com/libming/libming/issues/111
