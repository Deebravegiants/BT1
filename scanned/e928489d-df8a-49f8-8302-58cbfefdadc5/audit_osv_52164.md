# [H] CVE-2021-47148

## Summary
Severity: High
Advisory: CVE-2021-47148
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47148
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: fix a buffer overflow in otx2_set_rxfh_context()

This function is called from ethtool_set_rxfh() and "*rss_context"
comes from the user.  Add some bounds checking to prevent memory
corruption.

## References
- https://git.kernel.org/stable/c/389146bc6d2bbb20714d06624b74856320ce40f7
- https://git.kernel.org/stable/c/e5cc361e21648b75f935f9571d4003aaee480214
