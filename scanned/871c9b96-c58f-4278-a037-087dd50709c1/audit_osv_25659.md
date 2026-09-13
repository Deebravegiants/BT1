# [H] ksmbd: fix wrong next length validation of ea buffer in smb2_set_ea()

## Summary
Severity: High
Advisory: CVE-2023-4130
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2023-4130
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.127, >=5.16.0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix wrong next length validation of ea buffer in smb2_set_ea()

There are multiple smb2_ea_info buffers in FILE_FULL_EA_INFORMATION request
from client. ksmbd find next smb2_ea_info using ->NextEntryOffset of
current smb2_ea_info. ksmbd need to validate buffer length Before
accessing the next ea. ksmbd should check buffer length using buf_len,
not next variable. next is the start offset of current ea that got from
previous ea.

## References
- https://git.kernel.org/stable/c/4bf629262f9118ee91b1c3a518ebf2b3bcb22180
- https://git.kernel.org/stable/c/79ed288cef201f1f212dfb934bcaac75572fb8f6
- https://git.kernel.org/stable/c/aeb974907642be095e38ecb1a400ca583958b2b0
- https://git.kernel.org/stable/c/f339d76a3a972601d0738b881b099d49ebbdc3a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4130.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4130
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
