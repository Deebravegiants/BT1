# [H] smb: client: set correct id, uid and cruid for multiuser automounts

## Summary
Severity: High
Advisory: CVE-2024-26822
Ecosystem: Linux
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26822
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.201, >=5.16.0 <6.1.164, >=6.2.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: set correct id, uid and cruid for multiuser automounts

When uid, gid and cruid are not specified, we need to dynamically
set them into the filesystem context used for automounting otherwise
they'll end up reusing the values from the parent mount.

## References
- https://git.kernel.org/stable/c/2ceba8ae1bd1f5589548cb722a5c583ca3a2dede
- https://git.kernel.org/stable/c/4508ec17357094e2075f334948393ddedbb75157
- https://git.kernel.org/stable/c/4a6e4c56721a3e6e2550b72ec56aab306c4607a7
- https://git.kernel.org/stable/c/7590ba9057c6d74c66f3b909a383ec47cd2f27fb
- https://git.kernel.org/stable/c/c2aa2718cda2d56b4a551cb40043e9abc9684626
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26822.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26822
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
