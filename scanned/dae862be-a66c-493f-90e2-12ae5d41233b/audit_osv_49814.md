# [H] CVE-2019-19378

## Summary
Severity: High
Advisory: CVE-2019-19378
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2019-19378
Type: osv

## Details
In the Linux kernel 5.0.21, mounting a crafted btrfs filesystem image can lead to slab-out-of-bounds write access in index_rbio_pages in fs/btrfs/raid56.c.

## References
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19378
