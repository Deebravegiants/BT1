# [M] icmp: Fix data-races around sysctl_icmp_echo_enable_probe.

## Summary
Severity: Medium
Advisory: CVE-2022-49633
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49633
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

icmp: Fix data-races around sysctl_icmp_echo_enable_probe.

While reading sysctl_icmp_echo_enable_probe, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/05c615033174f1d19374f42285ccd8e9af13e427
- https://git.kernel.org/stable/c/4a2f7083cc6cb72dade9a63699ca352fad26d1cd
- https://git.kernel.org/stable/c/cce955efa0ab81f7fb72e22beed372054c86005c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49633.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49633
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
