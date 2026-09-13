# [M] tcp: Fix a data-race around sysctl_tcp_mtu_probe_floor.

## Summary
Severity: Medium
Advisory: CVE-2022-49594
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49594
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix a data-race around sysctl_tcp_mtu_probe_floor.

While reading sysctl_tcp_mtu_probe_floor, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/033963b220633ed1602d458e7e4ac06afa9fefb2
- https://git.kernel.org/stable/c/8e92d4423615a5257d0d871fc067aa561f597deb
- https://git.kernel.org/stable/c/cc36c37f5fe066c4708e623ead96dc8f57224bf5
- https://git.kernel.org/stable/c/d5bece4df6090395f891110ef52a6f82d16685db
- https://git.kernel.org/stable/c/e2ecbf3f0aa88277d43908c53b99399d55729ff9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49594.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49594
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
