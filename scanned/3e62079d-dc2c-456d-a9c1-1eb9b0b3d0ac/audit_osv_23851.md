# [M] tcp: Fix a data-race around sysctl_tcp_thin_linear_timeouts.

## Summary
Severity: Medium
Advisory: CVE-2022-49575
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49575
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix a data-race around sysctl_tcp_thin_linear_timeouts.

While reading sysctl_tcp_thin_linear_timeouts, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/404c53ccdebd11f96954f4070cffac8e0b4d5cb6
- https://git.kernel.org/stable/c/492f3713b282c0e67e951cd804edd22eccc25412
- https://git.kernel.org/stable/c/7c6f2a86ca590d5187a073d987e9599985fb1c7c
- https://git.kernel.org/stable/c/a0f96c4f179cb3560078cefccef105e8f1701210
- https://git.kernel.org/stable/c/cc133e4f4bc225079198192623945bb872c08143
- https://git.kernel.org/stable/c/f4b0295be9a3c4260de4585fac4062e602a88ac7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49575.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49575
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
