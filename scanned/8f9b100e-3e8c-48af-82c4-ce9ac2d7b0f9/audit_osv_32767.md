# [H] ublk: fix race between io_uring_cmd_complete_in_task and ublk_cancel_cmd

## Summary
Severity: High
Advisory: CVE-2025-37906
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37906
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ublk: fix race between io_uring_cmd_complete_in_task and ublk_cancel_cmd

ublk_cancel_cmd() calls io_uring_cmd_done() to complete uring_cmd, but
we may have scheduled task work via io_uring_cmd_complete_in_task() for
dispatching request, then kernel crash can be triggered.

Fix it by not trying to canceling the command if ublk block request is
started.

## References
- https://git.kernel.org/stable/c/f40139fde5278d81af3227444fd6e76a76b9506d
- https://git.kernel.org/stable/c/fb2eb9ddf556f93fef45201e1f9d2b8674bcc975
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37906.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37906
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
