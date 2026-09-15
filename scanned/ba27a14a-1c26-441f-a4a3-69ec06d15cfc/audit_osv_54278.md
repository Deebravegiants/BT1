# [H] CVE-2023-45871

## Summary
Severity: High
Advisory: CVE-2023-45871
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-15
Source: https://osv.dev/vulnerability/CVE-2023-45871
Type: osv

## Details
An issue was discovered in drivers/net/ethernet/intel/igb/igb_main.c in the IGB driver in the Linux kernel before 6.5.3. A buffer size may not be adequate for frames larger than the MTU.

## References
- https://security.netapp.com/advisory/ntap-20231110-0001/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.3
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=bb5ed01cd2428cd25b1c88a3a9cba87055eb289f
