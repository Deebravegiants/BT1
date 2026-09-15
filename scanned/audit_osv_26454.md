# [M] smb: client: fix warning in cifs_smb3_do_mount()

## Summary
Severity: Medium
Advisory: CVE-2023-53230
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53230
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.128, >=5.16.0 <6.1.47, >=5.19.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix warning in cifs_smb3_do_mount()

This fixes the following warning reported by kernel test robot

  fs/smb/client/cifsfs.c:982 cifs_smb3_do_mount() warn: possible
  memory leak of 'cifs_sb'

## References
- https://git.kernel.org/stable/c/12c30f33cc6769bf411088a2872843c4f9ea32f9
- https://git.kernel.org/stable/c/945f4a7aff84fde1f825d17a5050880345da3228
- https://git.kernel.org/stable/c/9850867042674361f455ea8901375cff5b800be5
- https://git.kernel.org/stable/c/eb79f8dfba343667f9a82a252743f4e8f67ce420
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53230.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53230
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
