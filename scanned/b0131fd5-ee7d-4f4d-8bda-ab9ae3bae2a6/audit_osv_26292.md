# [C] ksmbd: fix slab out of bounds write in smb_inherit_dacl()

## Summary
Severity: Critical
Advisory: CVE-2023-52755
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52755
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix slab out of bounds write in smb_inherit_dacl()

slab out-of-bounds write is caused by that offsets is bigger than pntsd
allocation size. This patch add the check to validate 3 offsets using
allocation size.

## References
- https://git.kernel.org/stable/c/09d9d8b40a3338193619c14ed4dc040f4f119e70
- https://git.kernel.org/stable/c/712e01f32e577e7e48ab0adb5fe550646a3d93cb
- https://git.kernel.org/stable/c/8387c94d73ec66eb597c7a23a8d9eadf64bfbafa
- https://git.kernel.org/stable/c/aaf0a07d60887d6c36fc46a24de0083744f07819
- https://git.kernel.org/stable/c/eebff19acaa35820cb09ce2ccb3d21bee2156ffb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52755.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52755
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
