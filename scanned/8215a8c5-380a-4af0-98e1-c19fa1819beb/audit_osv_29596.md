# [H] fou: remove warn in gue_gro_receive on unsupported protocol

## Summary
Severity: High
Advisory: CVE-2024-44940
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-44940
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.234, >=5.11.0 <5.15.174, >=5.16.0 <6.1.107, >=6.2.0 <6.6.47, >=6.7.0 <6.10.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fou: remove warn in gue_gro_receive on unsupported protocol

Drop the WARN_ON_ONCE inn gue_gro_receive if the encapsulated type is
not known or does not have a GRO handler.

Such a packet is easily constructed. Syzbot generates them and sets
off this warning.

Remove the warning as it is expected and not actionable.

The warning was previously reduced from WARN_ON to WARN_ON_ONCE in
commit 270136613bf7 ("fou: Do WARN_ON_ONCE in gue_gro_receive for bad
proto callbacks").

## References
- https://git.kernel.org/stable/c/3db4395332e7050ef9ddeb3052e6b5019f2a2a59
- https://git.kernel.org/stable/c/440ab7f97261bc28501636a13998e1b1946d2e79
- https://git.kernel.org/stable/c/5a2e37bc648a2503bf6d687aed27b9f4455d82eb
- https://git.kernel.org/stable/c/a925a200299a6dfc7c172f54da6f374edc930053
- https://git.kernel.org/stable/c/b1453a5616c7bd8acd90633ceba4e59105ba3b51
- https://git.kernel.org/stable/c/dd89a81d850fa9a65f67b4527c0e420d15bf836c
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44940.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44940
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
