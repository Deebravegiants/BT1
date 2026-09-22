# [M] tcp: Fix data-races around sysctl_tcp_slow_start_after_idle.

## Summary
Severity: Medium
Advisory: CVE-2022-49572
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49572
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.18 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_slow_start_after_idle.

While reading sysctl_tcp_slow_start_after_idle, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/0e3f82a03ec8c3808e87283e12946227415706c9
- https://git.kernel.org/stable/c/369d99c2b89f54473adcf9acdf40ea562b5a6e0e
- https://git.kernel.org/stable/c/3b26e11b07a09b31247688bec61e2925d4a571b6
- https://git.kernel.org/stable/c/41aeba4506f6b70ec7500c6fe202731a4ba29fe5
- https://git.kernel.org/stable/c/4845b5713ab18a1bb6e31d1fbb4d600240b8b691
- https://git.kernel.org/stable/c/68b6f9506747d507c7bfa374d178929b4157e8c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49572.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49572
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
