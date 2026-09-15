# [H] CVE-2023-1077

## Summary
Severity: High
Advisory: CVE-2023-1077
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-1077
Type: osv

## Details
In the Linux kernel, pick_next_rt_entity() may return a type confused entry, not detected by the BUG_ON condition, as the confused entry will not be NULL, but list_head.The buggy error condition would lead to a type confused entry with the list head,which would then be used as a type confused sched_rt_entity,causing memory corruption.

## References
- https://security.netapp.com/advisory/ntap-20230511-0002/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/?id=7c4a5b89a0b5a57a64b601775b296abf77a9fe97
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
