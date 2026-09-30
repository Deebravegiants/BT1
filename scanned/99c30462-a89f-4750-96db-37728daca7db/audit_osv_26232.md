# [H] ocfs2: Avoid touching renamed directory if parent does not change

## Summary
Severity: High
Advisory: CVE-2023-52590
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52590
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: Avoid touching renamed directory if parent does not change

The VFS will not be locking moved directory if its parent does not
change. Change ocfs2 rename code to avoid touching renamed directory if
its parent does not change as without locking that can corrupt the
filesystem.

## References
- https://git.kernel.org/stable/c/9d618d19b29c2943527e3a43da0a35aea91062fc
- https://git.kernel.org/stable/c/de940cede3c41624e2de27f805b490999f419df9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52590.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52590
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
