# [H] ipv6: guard against possible NULL deref in __in6_dev_stats_get()

## Summary
Severity: High
Advisory: CVE-2026-80646
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80646
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: guard against possible NULL deref in __in6_dev_stats_get()

dev_get_by_index_rcu() could return NULL if the original physical
device is unregistered.

Found by Sashiko.

## References
- https://git.kernel.org/stable/c/0db1949084e85a72d174a7dea3259b94fe5a9305
- https://git.kernel.org/stable/c/1a4adfbeb47a212a64539137411f1ca168474d33
- https://git.kernel.org/stable/c/1e3db30a88815bae6e9d5db6f64ac735e615a07e
- https://git.kernel.org/stable/c/507541c2a8eeb76c02bd2511958f73a8cfa3e1bc
- https://git.kernel.org/stable/c/952426a83ca75cea25c09d58944abafaa3ebd242
- https://git.kernel.org/stable/c/a23f2c68c6635e41404f189f8f7ae910738cebdb
- https://git.kernel.org/stable/c/e14db43677946bf2095febd294bb3c13ab375ab7
- https://git.kernel.org/stable/c/fc920c0659cdea5afd8721c1155a51564859e075
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80646.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80646
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
