# [M] NFS: Fix an Oops in nfs_d_automount()

## Summary
Severity: Medium
Advisory: CVE-2022-50385
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50385
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Fix an Oops in nfs_d_automount()

When mounting from a NFSv4 referral, path->dentry can end up being a
negative dentry, so derive the struct nfs_server from the dentry
itself instead.

## References
- https://git.kernel.org/stable/c/35e3b6ae84935d0d7ff76cbdaa83411b0ad5e471
- https://git.kernel.org/stable/c/5458bc0f9df639d83471ca384152cc62dbee0aeb
- https://git.kernel.org/stable/c/6f3d56783fbed861e483736a7001bdafd0dddd53
- https://git.kernel.org/stable/c/b6fd25d64b0de27991d6bd677f0adf69ad6ff07a
- https://git.kernel.org/stable/c/f12377abac15fb4e8698225ac386894f8ae63598
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50385.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50385
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
