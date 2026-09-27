# [H] CVE-2019-19814

## Summary
Severity: High
Advisory: CVE-2019-19814
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-17
Source: https://osv.dev/vulnerability/CVE-2019-19814
Type: osv

## Details
In the Linux kernel 5.0.21, mounting a crafted f2fs filesystem image can cause __remove_dirty_segment slab-out-of-bounds write access because an array is bounded by the number of dirty types (8) but the array index can exceed this.

## References
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19814
