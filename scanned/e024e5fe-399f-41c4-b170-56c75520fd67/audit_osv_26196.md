# [H] ksmbd: fix uaf in smb20_oplock_break_ack

## Summary
Severity: High
Advisory: CVE-2023-52479
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52479
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.135, >=5.16.0 <6.1.57, >=6.2.0 <6.5.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix uaf in smb20_oplock_break_ack

drop reference after use opinfo.

## References
- https://git.kernel.org/stable/c/694e13732e830cbbfedb562e57f28644927c33fd
- https://git.kernel.org/stable/c/8226ffc759ea59f10067b9acdf7f94bae1c69930
- https://git.kernel.org/stable/c/c69813471a1ec081a0b9bf0c6bd7e8afd818afce
- https://git.kernel.org/stable/c/d5b0e9d3563e7e314a850e81f42b2ef6f39882f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52479.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52479
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
