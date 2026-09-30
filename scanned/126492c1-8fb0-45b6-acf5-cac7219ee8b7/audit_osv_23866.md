# [M] tcp: Fix a data-race around sysctl_tcp_probe_interval.

## Summary
Severity: Medium
Advisory: CVE-2022-49593
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49593
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.14.290, >=4.15.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix a data-race around sysctl_tcp_probe_interval.

While reading sysctl_tcp_probe_interval, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/2a85388f1d94a9f8b5a529118a2c5eaa0520d85c
- https://git.kernel.org/stable/c/73a11588751a2c13f25d9da8117efc9a79b1843f
- https://git.kernel.org/stable/c/80dabd089086e6553b7acfcff2ec223bdada87a1
- https://git.kernel.org/stable/c/b14cc8afbbcbc6dce4797913c0b85266b897f541
- https://git.kernel.org/stable/c/b3798d3519eda9c409bb0815b0102f27ec42468d
- https://git.kernel.org/stable/c/c61aede097d350d890fa1edc9521b0072e14a0b8
- https://git.kernel.org/stable/c/e6b6f027e2854a51f345a5e3e808d7a88001d4f8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49593.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49593
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
