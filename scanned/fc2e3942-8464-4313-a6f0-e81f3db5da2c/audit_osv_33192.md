# [H] hsr: hold rcu and dev lock for hsr_get_port_ndev

## Summary
Severity: High
Advisory: CVE-2025-39872
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39872
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.64, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

hsr: hold rcu and dev lock for hsr_get_port_ndev

hsr_get_port_ndev calls hsr_for_each_port, which need to hold rcu lock.
On the other hand, before return the port device, we need to hold the
device reference to avoid UaF in the caller function.

## References
- https://git.kernel.org/stable/c/68a6729afd3e8e9a2a32538642ce92b96ccf9b1d
- https://git.kernel.org/stable/c/847748fc66d08a89135a74e29362a66ba4e3ab15
- https://git.kernel.org/stable/c/9433ba79c2ec3ec7c9a711748701549339c3438c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39872.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
