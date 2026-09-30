# [H] xfs: avoid dereferencing log items after push callbacks

## Summary
Severity: High
Advisory: CVE-2026-31453
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31453
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: avoid dereferencing log items after push callbacks

After xfsaild_push_item() calls iop_push(), the log item may have been
freed if the AIL lock was dropped during the push. Background inode
reclaim or the dquot shrinker can free the log item while the AIL lock
is not held, and the tracepoints in the switch statement dereference
the log item after iop_push() returns.

Fix this by capturing the log item type, flags, and LSN before calling
xfsaild_push_item(), and introducing a new xfs_ail_push_class trace
event class that takes these pre-captured values and the ailp pointer
instead of the log item pointer.

## References
- https://git.kernel.org/stable/c/451c6329d9afa45862c36fe6677eb7750db60617
- https://git.kernel.org/stable/c/7121b22b0bac89394cc4c6a54b5aebc15347bdf5
- https://git.kernel.org/stable/c/79ef34ec0554ec04bdbafafbc9836423734e1bd6
- https://git.kernel.org/stable/c/95fb5d643cc70959baa54cd17f52f80ffc3295e7
- https://git.kernel.org/stable/c/c4d603e8e58a3bf35480135ccca2b4f7238abda5
- https://git.kernel.org/stable/c/c8a2ab339b88d10fc34a3318c92f07d8a467019d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31453.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31453
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
