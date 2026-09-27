# [H] ima: Fix use-after-free on a dentry's dname.name

## Summary
Severity: High
Advisory: CVE-2024-39494
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-39494
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.174, >=5.16.0 <6.1.97, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ima: Fix use-after-free on a dentry's dname.name

->d_name.name can change on rename and the earlier value can be freed;
there are conditions sufficient to stabilize it (->d_lock on dentry,
->d_lock on its parent, ->i_rwsem exclusive on the parent's inode,
rename_lock), but none of those are met at any of the sites. Take a stable
snapshot of the name instead.

## References
- https://git.kernel.org/stable/c/0b31e28fbd773aefb6164687e0767319b8199829
- https://git.kernel.org/stable/c/480afcbeb7aaaa22677d3dd48ec590b441eaac1a
- https://git.kernel.org/stable/c/7fb374981e31c193b1152ed8d3b0a95b671330d4
- https://git.kernel.org/stable/c/a78a6f0da57d058e2009e9958fdcef66f165208c
- https://git.kernel.org/stable/c/be84f32bb2c981ca670922e047cdde1488b233de
- https://git.kernel.org/stable/c/dd431c3ac1fc34a9268580dd59ad3e3c76b32a8c
- https://git.kernel.org/stable/c/edf287bc610b18d7a9c0c0c1cb2e97b9348c71bb
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39494.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39494
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
