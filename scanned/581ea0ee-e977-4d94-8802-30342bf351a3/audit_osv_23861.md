# [M] tcp: Fix a data-race around sysctl_tcp_notsent_lowat.

## Summary
Severity: Medium
Advisory: CVE-2022-49587
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49587
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.9.325, >=4.10.0 <4.14.290, >=4.15.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix a data-race around sysctl_tcp_notsent_lowat.

While reading sysctl_tcp_notsent_lowat, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/0f75343584ee474303e17efe0610bdd170af1d13
- https://git.kernel.org/stable/c/55be873695ed8912eb77ff46d1d1cadf028bd0f3
- https://git.kernel.org/stable/c/62e56cfeb2ae4b53ae9ca24c80f54093250ce64a
- https://git.kernel.org/stable/c/80d4d0c461674eea87f0977e12a2ecd334b9b79c
- https://git.kernel.org/stable/c/91e21df688f8a75255ca9c459da39ac96300113a
- https://git.kernel.org/stable/c/c1b85c5a34294f7444c13bf828e0e84b0a0eed85
- https://git.kernel.org/stable/c/e9362a993886613ef0284c2a4911c6017c97d803
- https://git.kernel.org/stable/c/fd6f1284e380c377932186042ff0b5c987fb2b92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49587.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49587
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
