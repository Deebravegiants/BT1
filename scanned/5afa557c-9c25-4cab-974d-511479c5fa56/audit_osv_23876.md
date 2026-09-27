# [M] ip: Fix data-races around sysctl_ip_fwd_update_priority.

## Summary
Severity: Medium
Advisory: CVE-2022-49603
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49603
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip: Fix data-races around sysctl_ip_fwd_update_priority.

While reading sysctl_ip_fwd_update_priority, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/11038fa781ab916535c53351537b22d6d405667d
- https://git.kernel.org/stable/c/351f81f7d7185d18a9ff76f8f8c2fa8c4eea563b
- https://git.kernel.org/stable/c/7bf9e18d9a5e99e3c83482973557e9f047b051e7
- https://git.kernel.org/stable/c/bcc03369d3277ae075ed421f0c8bf4adb5e65b74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49603.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49603
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
