# [H] ksmbd: fix NULL pointer dereference in smb2_get_info_filesystem()

## Summary
Severity: High
Advisory: CVE-2023-53399
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53399
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix NULL pointer dereference in smb2_get_info_filesystem()

If share is , share->path is NULL and it cause NULL pointer
dereference issue.

## References
- https://git.kernel.org/stable/c/1636e09779f83e10e6ed57d91ef94abcefdd206b
- https://git.kernel.org/stable/c/227eb2689b44d0d60da3839b146983e73435924c
- https://git.kernel.org/stable/c/3ac00a2ab69b34189942afa9e862d5170cdcb018
- https://git.kernel.org/stable/c/a70751dd7b60eab025e97e19b6b2477c6eaf2bbb
- https://git.kernel.org/stable/c/b35f6c031b87d9e51f141ff6de0ea59756a8e313
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53399.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53399
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
