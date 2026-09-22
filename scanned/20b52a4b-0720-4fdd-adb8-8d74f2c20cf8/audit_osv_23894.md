# [M] icmp: Fix a data-race around sysctl_icmp_errors_use_inbound_ifaddr.

## Summary
Severity: Medium
Advisory: CVE-2022-49632
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49632
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

icmp: Fix a data-race around sysctl_icmp_errors_use_inbound_ifaddr.

While reading sysctl_icmp_errors_use_inbound_ifaddr, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/d2efabce81db7eed1c98fa1a3f203f0edd738ac3
- https://git.kernel.org/stable/c/de9490c32bc10020efdd1509689a28f197d6dfb8
- https://git.kernel.org/stable/c/f9617844e4d5d6331dbce3fb19a24e5bda201e58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49632.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49632
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
