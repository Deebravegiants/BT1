# [M] netfilter: nft_socket: remove WARN_ON_ONCE on maximum cgroup level

## Summary
Severity: Medium
Advisory: CVE-2024-56783
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56783
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_socket: remove WARN_ON_ONCE on maximum cgroup level

cgroup maximum depth is INT_MAX by default, there is a cgroup toggle to
restrict this maximum depth to a more reasonable value not to harm
performance. Remove unnecessary WARN_ON_ONCE which is reachable from
userspace.

## References
- https://git.kernel.org/stable/c/2f9bec0a749eb646b384fde0c7b7c24687b2ffae
- https://git.kernel.org/stable/c/7064a6daa4a700a298fe3aee11dea296bfe59fc4
- https://git.kernel.org/stable/c/b7529880cb961d515642ce63f9d7570869bbbdc3
- https://git.kernel.org/stable/c/e227c042580ab065edc610c9ddc9bea691e6fc4d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56783.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56783
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
