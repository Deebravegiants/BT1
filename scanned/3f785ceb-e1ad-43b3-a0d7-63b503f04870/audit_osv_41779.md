# [H] RDMA/core: Prefer NLA_NUL_STRING

## Summary
Severity: High
Advisory: CVE-2026-63860
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63860
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/core: Prefer NLA_NUL_STRING

These attributes are evaluated as c-string (passed to strcmp), but
NLA_STRING doesn't check for the presence of a \0 terminator.

Either this needs to switch to nla_strcmp() and needs to adjust printf fmt
specifier to not use plain %s, or this needs to use NLA_NUL_STRING.

As the code has been this way for long time, it seems to me that userspace
does include the terminating nul, even tough its not enforced so far, and
thus NLA_NUL_STRING use is the simpler solution.

## References
- https://git.kernel.org/stable/c/137b5918931d4d05aa8ea8d3adf67f7224eef63c
- https://git.kernel.org/stable/c/5877c043398d5fa0e93919a3d837e5cd7a98a961
- https://git.kernel.org/stable/c/6ed3d14fc45d3da6025e7fe4a6a09066856698e2
- https://git.kernel.org/stable/c/87111356d58d86edb221ba144d261ed83a5b8bbe
- https://git.kernel.org/stable/c/abda65bdd13084c771842adaac1f652d0660dd82
- https://git.kernel.org/stable/c/c26a0052cceed4c4d380ee5808b699f937fb58d8
- https://git.kernel.org/stable/c/f2c7b39dde2e61df8157066969cc2a408cd3dcd9
- https://git.kernel.org/stable/c/fcd07d3b8ee7a39b344d73aed69c1a68cd9eacdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63860.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63860
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
