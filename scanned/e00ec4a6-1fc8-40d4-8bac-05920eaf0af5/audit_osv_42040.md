# [C] ksmbd: use opener credentials for ADS I/O

## Summary
Severity: Critical
Advisory: CVE-2026-64391
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64391
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: use opener credentials for ADS I/O

Alternate data streams are stored as xattrs. Unlike regular file I/O,
their read and write paths therefore call VFS xattr helpers which recheck
inode permissions and LSM policy using the current task credentials.

Run ADS I/O with the credentials captured when the SMB handle was opened.

## References
- https://git.kernel.org/stable/c/2b4592cea214683de0f2ce6f8c22c097fb0ea1ab
- https://git.kernel.org/stable/c/52a56cf53ec834c44ac1b4d16d585f26613ee5ce
- https://git.kernel.org/stable/c/a8f5d39971bbad9340d49cd41b0e2da9452a649d
- https://git.kernel.org/stable/c/baa5e094886fffa7e6272edcb5e08be5ce28262c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64391.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64391
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
