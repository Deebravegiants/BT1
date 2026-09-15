# [H] CVE-2021-38207

## Summary
Severity: High
Advisory: CVE-2021-38207
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38207
Type: osv

## Details
drivers/net/ethernet/xilinx/ll_temac_main.c in the Linux kernel before 5.12.13 allows remote attackers to cause a denial of service (buffer overflow and lockup) by sending heavy network traffic for about ten minutes.

## References
- https://security.netapp.com/advisory/ntap-20210902-0007/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.13
- https://github.com/torvalds/linux/commit/c364df2489b8ef2f5e3159b1dff1ff1fdb16040d
