# [M] CVE-2020-28097

## Summary
Severity: Medium
Advisory: CVE-2020-28097
CVSS: 5.9 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2020-28097
Type: osv

## Details
The vgacon subsystem in the Linux kernel before 5.8.10 mishandles software scrollback. There is a vgacon_scrolldelta out-of-bounds read, aka CID-973c096f6a85.

## References
- https://security.netapp.com/advisory/ntap-20210805-0001/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=973c096f6a85e5b5f2a295126ba6928d9a6afd45
- https://github.com/torvalds/linux/commit/973c096f6a85e5b5f2a295126ba6928d9a6afd45
- https://seclists.org/oss-sec/2020/q3/176
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.10
