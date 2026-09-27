# [C] smb: client: fix potential UAF in smb2_is_valid_oplock_break()

## Summary
Severity: Critical
Advisory: CVE-2024-35865
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35865
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.15.209, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential UAF in smb2_is_valid_oplock_break()

Skip sessions that are being teared down (status == SES_EXITING) to
avoid UAF.

## References
- https://git.kernel.org/stable/c/21fed37d2bdcde33453faf61d3d4d96c355f04bd
- https://git.kernel.org/stable/c/22863485a4626ec6ecf297f4cc0aef709bc862e4
- https://git.kernel.org/stable/c/3dba0e5276f131e36d6d8043191d856f49238628
- https://git.kernel.org/stable/c/84488466b7a69570bdbf76dd9576847ab97d54e7
- https://git.kernel.org/stable/c/a710ef9e974f18232d2b9b19c90eda1a1167b2d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35865.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35865
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
