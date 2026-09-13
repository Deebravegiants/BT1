# [H] jfs: fix slab-out-of-bounds Read in dtSearch

## Summary
Severity: High
Advisory: CVE-2023-52602
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52602
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: fix slab-out-of-bounds Read in dtSearch

Currently while searching for current page in the sorted entry table
of the page there is a out of bound access. Added a bound check to fix
the error.

Dave:
Set return code to -EIO

## References
- https://git.kernel.org/stable/c/1b9d6828589d57f94a23fb1c46112cda39d7efdb
- https://git.kernel.org/stable/c/1c40ca3d39d769931b28295b3145c25f1decf5a6
- https://git.kernel.org/stable/c/6c6a96c3d74df185ee344977d46944d6f33bb4dd
- https://git.kernel.org/stable/c/7110650b85dd2f1cee819acd1345a9013a1a62f7
- https://git.kernel.org/stable/c/bff9d4078a232c01e42e9377d005fb2f4d31a472
- https://git.kernel.org/stable/c/cab0c265ba182fd266c2aa3c69d7e40640a7f612
- https://git.kernel.org/stable/c/ce8bc22e948634a5c0a3fa58a179177d0e3f3950
- https://git.kernel.org/stable/c/fa5492ee89463a7590a1449358002ff7ef63529f
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52602.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52602
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
