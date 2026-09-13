# [M] tcp: Fix a data-race around sysctl_tcp_early_retrans.

## Summary
Severity: Medium
Advisory: CVE-2022-49573
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49573
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix a data-race around sysctl_tcp_early_retrans.

While reading sysctl_tcp_early_retrans, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/11e8b013d16e5db63f8f76acceb5b86964098aaa
- https://git.kernel.org/stable/c/488d3ad98ef7cddce7054193dbae6b4349c6807d
- https://git.kernel.org/stable/c/5037ca9e4b169cc9aed0174d658c3d81fdaf8ea5
- https://git.kernel.org/stable/c/52e65865deb6a36718a463030500f16530eaab74
- https://git.kernel.org/stable/c/83767fe800a311370330d4ec83aa76093b744a80
- https://git.kernel.org/stable/c/d5975f6376ce90c2c483ae36bf88c9cface4c13b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49573.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49573
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
