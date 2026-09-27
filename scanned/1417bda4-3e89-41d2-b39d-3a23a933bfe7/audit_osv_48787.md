# [H] CVE-2018-13348

## Summary
Severity: High
Advisory: CVE-2018-13348
Aliases: GHSA-3v62-ww8w-758m, PYSEC-2018-90
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-06
Source: https://osv.dev/vulnerability/CVE-2018-13348
Type: osv

## Details
The mpatch_decode function in mpatch.c in Mercurial before 4.6.1 mishandles certain situations where there should be at least 12 bytes remaining after the current position in the patch data, but actually are not, aka OVE-20180430-0001.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00032.html
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_4.6.1_.282018-06-06.29
- https://www.mercurial-scm.org/repo/hg/rev/90a274965de7
