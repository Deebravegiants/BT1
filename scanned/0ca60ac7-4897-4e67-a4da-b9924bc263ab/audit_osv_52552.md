# [M] CVE-2021-47570

## Summary
Severity: Medium
Advisory: CVE-2021-47570
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47570
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: r8188eu: fix a memory leak in rtw_wx_read32()

Free "ptmp" before returning -EINVAL.

## References
- https://git.kernel.org/stable/c/be4ea8f383551b9dae11b8dfff1f38b3b5436e9a
- https://git.kernel.org/stable/c/c8d3775745adacf9784a7a80a82d047051752573
