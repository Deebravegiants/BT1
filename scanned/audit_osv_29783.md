# [C] smb: client: fix double put of @cfile in smb2_rename_path()

## Summary
Severity: Critical
Advisory: CVE-2024-46736
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46736
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix double put of @cfile in smb2_rename_path()

If smb2_set_path_attr() is called with a valid @cfile and returned
-EINVAL, we need to call cifs_get_writable_path() again as the
reference of @cfile was already dropped by previous smb2_compound_op()
call.

## References
- https://git.kernel.org/stable/c/1a46c7f6546b73cbf36f5a618a1a6bbb45391eb3
- https://git.kernel.org/stable/c/3523a3df03c6f04f7ea9c2e7050102657e331a4f
- https://git.kernel.org/stable/c/b27ea9c96efd2c252a981fb00d0f001b86c90f3e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46736.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46736
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
