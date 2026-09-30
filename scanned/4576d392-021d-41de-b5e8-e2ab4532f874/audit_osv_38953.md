# [H] procfs: fix possible double mmput() in do_procmap_query()

## Summary
Severity: High
Advisory: CVE-2026-43178
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43178
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

procfs: fix possible double mmput() in do_procmap_query()

When user provides incorrectly sized buffer for build ID for PROCMAP_QUERY
we return with -ENAMETOOLONG error.  After recent changes this condition
happens later, after we unlocked mmap_lock/per-VMA lock and did mmput(),
so original goto out is now wrong and will double-mmput() mm_struct.  Fix
by jumping further to clean up only vm_file and name_buf.

## References
- https://git.kernel.org/stable/c/61dc9f776705d6db6847c101b98fa4f0e9eb6fa3
- https://git.kernel.org/stable/c/8adaff87db143583e08eec4f4e7788f1ef8af94d
- https://git.kernel.org/stable/c/90f5e87c9b75833b9ef3a4415b92c0247f28ab2f
- https://git.kernel.org/stable/c/f9fe092084cd04deea18747f58a2304026e76aaa
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43178.json
- https://access.redhat.com/security/cve/CVE-2026-43178
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43178.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43178
- https://bugzilla.redhat.com/show_bug.cgi?id=2467227
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
