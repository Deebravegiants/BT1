# [H] ntfs3: reject direct userspace writes to reserved $LX* xattrs

## Summary
Severity: High
Advisory: CVE-2026-63833
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63833
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs3: reject direct userspace writes to reserved $LX* xattrs

NTFS3 uses $LXUID, $LXGID, $LXMOD and $LXDEV as internal WSL
permission metadata and reloads them into i_uid, i_gid and i_mode
from ntfs_get_wsl_perm().

Because the empty-prefix xattr handler also lets file owners call
setxattr() on these names directly, an unprivileged writer on a
writable ntfs3 mount can plant root ownership and S_ISUID on their own
file and gain euid 0 after inode reload.

Reject direct userspace writes to the reserved $LX* names. Internal
ntfs3 metadata updates are unchanged because ntfs_save_wsl_perm()
writes them via ntfs_set_ea() directly.

[almaz.alexandrovich@paragon-software.com: added an additional check for non privileged users]

## References
- https://git.kernel.org/stable/c/293a84fa40b3a1b3471c0545722724bc10973f76
- https://git.kernel.org/stable/c/2c3cd6da4a14380ef79e34bd9dff7caf46687477
- https://git.kernel.org/stable/c/5b08dccecf825cbf905f348bc6ccb497507e28e2
- https://git.kernel.org/stable/c/5e658b9245a52d838ef93729a7bc07de8e19deb7
- https://git.kernel.org/stable/c/e574af95234afc3c725988bbc1fdeb46b9f386a4
- https://git.kernel.org/stable/c/e8852ae29868e449fdb47eebc28f35fb80741a5f
- https://git.kernel.org/stable/c/f8d420949b335a4b51d06ab276beee6b8dfdc909
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63833.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63833
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
