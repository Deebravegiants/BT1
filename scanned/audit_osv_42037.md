# [H] smb/client: fix chown/chgrp with SMB3 POSIX Extensions

## Summary
Severity: High
Advisory: CVE-2026-64388
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64388
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/client: fix chown/chgrp with SMB3 POSIX Extensions

Ownership (chown) and group (chgrp) modifications were being ignored when
mounting with SMB3 POSIX Extensions unless CIFS_MOUNT_CIFS_ACL or
CIFS_MOUNT_MODE_FROM_SID were also explicitly set.

Fix this by checking for posix_extensions in cifs_setattr_nounix() when
updating UID and GID, ensuring that id_mode_to_cifs_acl() is called to map
and set the ownership/group information on the server.

## References
- https://git.kernel.org/stable/c/550cfb8a81181331d4d0f76ab75ee58a0bf41e3e
- https://git.kernel.org/stable/c/760ef2c579c2609cf17fb1cd5392f64d42d43d33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64388.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64388
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
