# [M] Bluetooth: Add check for mgmt_alloc_skb() in mgmt_remote_name()

## Summary
Severity: Medium
Advisory: CVE-2025-21937
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21937
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Add check for mgmt_alloc_skb() in mgmt_remote_name()

Add check for the return value of mgmt_alloc_skb() in
mgmt_remote_name() to prevent null pointer dereference.

## References
- https://git.kernel.org/stable/c/37785a01040cb5d11ed0ddbcbf78491fcd073161
- https://git.kernel.org/stable/c/69fb168b88e4d62cb31cdd725b67ccc5216cfcaf
- https://git.kernel.org/stable/c/88310caff68ae69d0574859f7926a59c1da2d60b
- https://git.kernel.org/stable/c/c5845c73cbacf5704169283ef29ca02031a36564
- https://git.kernel.org/stable/c/f2176a07e7b19f73e05c805cf3d130a2999154cb
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21937.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21937
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
