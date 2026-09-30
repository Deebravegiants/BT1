# [M] CVE-2019-16089

## Summary
Severity: Medium
Advisory: CVE-2019-16089
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-16089
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.2.13. nbd_genl_status in drivers/block/nbd.c does not check the nla_nest_start_noflag return value.

## References
- https://support.f5.com/csp/article/K03814795?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4414-1/
- https://usn.ubuntu.com/4425-1/
- https://usn.ubuntu.com/4439-1/
- https://usn.ubuntu.com/4440-1/
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://lore.kernel.org/patchwork/patch/1126650/
- https://lore.kernel.org/patchwork/patch/1106884/
