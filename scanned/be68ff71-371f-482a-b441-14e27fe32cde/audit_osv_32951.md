# [C] netfs: Fix double put of request

## Summary
Severity: Critical
Advisory: CVE-2025-38411
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38411
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.3 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix double put of request

If a netfs request finishes during the pause loop, it will have the ref
that belongs to the IN_PROGRESS flag removed at that point - however, if it
then goes to the final wait loop, that will *also* put the ref because it
sees that the IN_PROGRESS flag is clear and incorrectly assumes that this
happened when it called the collector.

In fact, since IN_PROGRESS is clear, we shouldn't call the collector again
since it's done all the cleanup, such as calling ->ki_complete().

Fix this by making netfs_collect_in_app() just return, indicating that
we're done if IN_PROGRESS is removed.

## References
- https://git.kernel.org/stable/c/9df7b5ebead649b00bf9a53a798e4bf83a1318fd
- https://git.kernel.org/stable/c/d18facba5a5795ad44b2a00a052e3db2fa77ab12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38411.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38411
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
