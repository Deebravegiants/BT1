# [M] CVE-2018-10689

## Summary
Severity: Medium
Advisory: CVE-2018-10689
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-03
Source: https://osv.dev/vulnerability/CVE-2018-10689
Type: osv

## Details
blktrace (aka Block IO Tracing) 1.2.0, as used with the Linux kernel and Android, has a buffer overflow in the dev_map_read function in btt/devmap.c because the device and devno arrays are too small, as demonstrated by an invalid free when using the btt program with a crafted file.

## References
- http://git.kernel.dk/?p=blktrace.git%3Ba=log%3Bh=d61ff409cb4dda31386373d706ea0cfb1aaac5b7
- https://security.gentoo.org/glsa/202107-15
- https://www.spinics.net/lists/linux-btrace/msg00847.html
- http://www.securityfocus.com/bid/104142
- https://access.redhat.com/errata/RHSA-2019:2162
- https://git.kernel.org/pub/scm/linux/kernel/git/axboe/blktrace.git/commit/?id=d61ff409cb4dda31386373d706ea0cfb1aaac5b7
