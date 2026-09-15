# [H] mailbox: mtk-cmdq: Fix pm_runtime_get_sync() warning in mbox shutdown

## Summary
Severity: High
Advisory: CVE-2024-39492
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-10
Source: https://osv.dev/vulnerability/CVE-2024-39492
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mailbox: mtk-cmdq: Fix pm_runtime_get_sync() warning in mbox shutdown

The return value of pm_runtime_get_sync() in cmdq_mbox_shutdown()
will return 1 when pm runtime state is active, and we don't want to
get the warning message in this case.

So we change the return value < 0 for WARN_ON().

## References
- https://git.kernel.org/stable/c/2d42a37a4518478f075ccf848242b4a50e313a46
- https://git.kernel.org/stable/c/747a69a119c469121385543f21c2d08562968ccc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39492.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39492
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
