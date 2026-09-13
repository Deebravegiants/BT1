# [C] smb: client: fix potential UAF in smb2_is_valid_lease_break()

## Summary
Severity: Critical
Advisory: CVE-2024-35864
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35864
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential UAF in smb2_is_valid_lease_break()

Skip sessions that are being teared down (status == SES_EXITING) to
avoid UAF.

## References
- https://git.kernel.org/stable/c/705c76fbf726c7a2f6ff9143d4013b18daaaebf1
- https://git.kernel.org/stable/c/a8344e2b69bde63f713b0aa796d70dbeadffddfb
- https://git.kernel.org/stable/c/c868cabdf6fdd61bea54532271f4708254e57fc5
- https://git.kernel.org/stable/c/f92739fdd4522c4291277136399353d7c341fae4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35864.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35864
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
