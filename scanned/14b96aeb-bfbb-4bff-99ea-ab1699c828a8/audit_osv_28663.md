# [C] smb: client: fix potential UAF in is_valid_oplock_break()

## Summary
Severity: Critical
Advisory: CVE-2024-35863
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35863
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential UAF in is_valid_oplock_break()

Skip sessions that are being teared down (status == SES_EXITING) to
avoid UAF.

## References
- https://git.kernel.org/stable/c/0a15ba88a32fa7a516aff7ffd27befed5334dff2
- https://git.kernel.org/stable/c/16d58c6a7db5050b9638669084b63fc05f951825
- https://git.kernel.org/stable/c/494c91e1e9413b407d12166a61b84200d4d54fac
- https://git.kernel.org/stable/c/69ccf040acddf33a3a85ec0f6b45ef84b0f7ec29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35863.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35863
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
