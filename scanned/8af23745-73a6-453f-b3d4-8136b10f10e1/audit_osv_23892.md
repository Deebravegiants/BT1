# [M] tcp: Fix a data-race around sysctl_tcp_ecn_fallback.

## Summary
Severity: Medium
Advisory: CVE-2022-49630
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49630
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix a data-race around sysctl_tcp_ecn_fallback.

While reading sysctl_tcp_ecn_fallback, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/12b8d9ca7e678abc48195294494f1815b555d658
- https://git.kernel.org/stable/c/1ec3d6c2626ee6e1b36b7bd006873a271406ba61
- https://git.kernel.org/stable/c/8bcf7339f2cf70ea4461df6ea045d1aadfabfa11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49630.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49630
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
