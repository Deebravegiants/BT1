# [H] ocfs2: fix slab-use-after-free due to dangling pointer dqi_priv

## Summary
Severity: High
Advisory: CVE-2024-57892
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57892
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix slab-use-after-free due to dangling pointer dqi_priv

When mounting ocfs2 and then remounting it as read-only, a
slab-use-after-free occurs after the user uses a syscall to
quota_getnextquota.  Specifically, sb_dqinfo(sb, type)->dqi_priv is the
dangling pointer.

During the remounting process, the pointer dqi_priv is freed but is never
set as null leaving it to be accessed.  Additionally, the read-only option
for remounting sets the DQUOT_SUSPENDED flag instead of setting the
DQUOT_USAGE_ENABLED flags.  Moreover, later in the process of getting the
next quota, the function ocfs2_get_next_id is called and only checks the
quota usage flags and not the quota suspended flags.

To fix this, I set dqi_priv to null when it is freed after remounting with
read-only and put a check for DQUOT_SUSPENDED in ocfs2_get_next_id.

[akpm@linux-foundation.org: coding-style cleanups]

## References
- https://git.kernel.org/stable/c/2d431192486367eee03cc28d0b53b97dafcb8e63
- https://git.kernel.org/stable/c/2e3d203b1adede46bbba049e497765d67865be18
- https://git.kernel.org/stable/c/58f9e20e2a7602e1dd649a1ec4790077c251cb6c
- https://git.kernel.org/stable/c/5f3fd772d152229d94602bca243fbb658068a597
- https://git.kernel.org/stable/c/8ff6f635a08c30559ded0c110c7ce03ba7747d11
- https://git.kernel.org/stable/c/ba950a02d8d23811aa1120affd3adedcfac6153d
- https://git.kernel.org/stable/c/f44e6d70c100614c211703f065cad448050e4a0e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57892.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57892
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
