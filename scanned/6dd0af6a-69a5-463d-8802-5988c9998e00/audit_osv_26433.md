# [M] ublk: fail to recover device if queue setup is interrupted

## Summary
Severity: Medium
Advisory: CVE-2023-53207
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53207
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.43, >=6.2.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ublk: fail to recover device if queue setup is interrupted

In ublk_ctrl_end_recovery(), if wait_for_completion_interruptible() is
interrupted by signal, queues aren't setup successfully yet, so we
have to fail UBLK_CMD_END_USER_RECOVERY, otherwise kernel oops can be
triggered.

## References
- https://git.kernel.org/stable/c/0c0cbd4ebc375ceebc75c89df04b74f215fab23a
- https://git.kernel.org/stable/c/84415f934ad4e96f3507fd09b831953d60fb04ec
- https://git.kernel.org/stable/c/b3a1e243a74632f88b22e713f1c7256754017d58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53207.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53207
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
