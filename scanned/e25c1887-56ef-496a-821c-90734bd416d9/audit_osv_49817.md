# [H] CVE-2019-19449

## Summary
Severity: High
Advisory: CVE-2019-19449
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-08
Source: https://osv.dev/vulnerability/CVE-2019-19449
Type: osv

## Details
In the Linux kernel 5.0.21, mounting a crafted f2fs filesystem image can lead to slab-out-of-bounds read access in f2fs_build_segment_manager in fs/f2fs/segment.c, related to init_min_max_mtime in fs/f2fs/segment.c (because the second argument to get_seg_entry is not validated).

## References
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19449
