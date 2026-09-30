# [C] ksmbd: fix out of bounds read in smb2_sess_setup

## Summary
Severity: Critical
Advisory: CVE-2023-3867
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2023-3867
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.145, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix out of bounds read in smb2_sess_setup

ksmbd does not consider the case of that smb2 session setup is
in compound request. If this is the second payload of the compound,
OOB read issue occurs while processing the first payload in
the smb2_sess_setup().

## References
- https://git.kernel.org/stable/c/2ba03cecb12ac7ac9e0170e251543c56832d9959
- https://git.kernel.org/stable/c/676392184785ace61e939831e7ca44a03d438c3b
- https://git.kernel.org/stable/c/98422bdd4cb3ca4d08844046f6507d7ec2c2b8d8
- https://git.kernel.org/stable/c/ef572ffa8eb44111eed2925fbb2adca78bdcbf61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3867.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3867
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
