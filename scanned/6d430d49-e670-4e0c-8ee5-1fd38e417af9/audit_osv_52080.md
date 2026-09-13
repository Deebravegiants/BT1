# [H] CVE-2021-47049

## Summary
Severity: High
Advisory: CVE-2021-47049
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47049
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

Drivers: hv: vmbus: Use after free in __vmbus_open()

The "open_info" variable is added to the &vmbus_connection.chn_msg_list,
but the error handling frees "open_info" without removing it from the
list.  This will result in a use after free.  First remove it from the
list, and then free it.

## References
- https://git.kernel.org/stable/c/d5c7b42c9f56ca46b286daa537d181bd7f69214f
- https://git.kernel.org/stable/c/f37dd5d1b5d38a79a4f7b8dd7bbb705505f05560
- https://git.kernel.org/stable/c/2728f289b3270b0e273292b46c534421a33bbfd5
- https://git.kernel.org/stable/c/3e9bf43f7f7a46f21ec071cb47be92d0874c48da
