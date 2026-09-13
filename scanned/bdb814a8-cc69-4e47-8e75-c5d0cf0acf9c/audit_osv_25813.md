# [C] ksmbd: validate command request size

## Summary
Severity: Critical
Advisory: CVE-2023-4515
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2023-4515
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.127, >=5.16.0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate command request size

In commit 2b9b8f3b68ed ("ksmbd: validate command payload size"), except
for SMB2_OPLOCK_BREAK_HE command, the request size of other commands
is not checked, it's not expected. Fix it by add check for request
size of other commands.

## References
- https://git.kernel.org/stable/c/595679098bdcdbfbba91ebe07a2f7f208df93870
- https://git.kernel.org/stable/c/5aa4fda5aa9c2a5a7bac67b4a12b089ab81fee3c
- https://git.kernel.org/stable/c/c6bef3bc30fd4a175aef846b7d928a6c40d091cd
- https://git.kernel.org/stable/c/ff7236b66d69582f90cf5616e63cfc3dc18142bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4515.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4515
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
