# [H] CVE-2019-15925

## Summary
Severity: High
Advisory: CVE-2019-15925
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15925
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.2.3. An out of bounds access exists in the function hclge_tm_schd_mode_vnet_base_cfg in the file drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.c.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.3
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://usn.ubuntu.com/4147-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=04f25edb48c441fc278ecc154c270f16966cbb90
