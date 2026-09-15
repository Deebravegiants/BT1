# [M] CVE-2017-14431

## Summary
Severity: Medium
Advisory: CVE-2017-14431
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-13
Source: https://osv.dev/vulnerability/CVE-2017-14431
Type: osv

## Details
Memory leak in Xen 3.3 through 4.8.x allows guest OS users to cause a denial of service (ARM or x86 AMD host OS memory consumption) by continually rebooting, because certain cleanup is skipped if no pass-through device was ever assigned, aka XSA-207.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00006.html
- https://xenbits.xen.org/xsa/advisory-207.html
