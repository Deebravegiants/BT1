# [H] ipv4: free net->ipv4.sysctl_local_reserved_ports after unregister_net_sysctl_table()

## Summary
Severity: High
Advisory: CVE-2026-64002
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64002
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: free net->ipv4.sysctl_local_reserved_ports after unregister_net_sysctl_table()

ipv4_sysctl_exit_net() is currently freeing net->ipv4.sysctl_local_reserved_ports
too soon.

Only after unregister_net_sysctl_table() we can be sure no threads can possibly
use the sysctls, including /proc/sys/net/ipv4/ip_local_reserved_ports.

## References
- https://git.kernel.org/stable/c/155f90be5ee8be5b110ebc0b7da33c54c83b0208
- https://git.kernel.org/stable/c/5b23a2ff379e70b6b9ff744a972b63e1f8f4d996
- https://git.kernel.org/stable/c/6512c57c4638ddec113bf42439361ba85a12048d
- https://git.kernel.org/stable/c/87a1e0fe7776da7ab411be332b4be58ac8840d10
- https://git.kernel.org/stable/c/8e59d4d0dcde2dfb07a7ef855c849a2a0560aa57
- https://git.kernel.org/stable/c/a0ffc6081a8b27082dd5eae5aa1e3f59bbecf06c
- https://git.kernel.org/stable/c/a7f4eefb6e1458431eef9fa20fb363320d185f76
- https://git.kernel.org/stable/c/ecf45080a4d3f4526cacb8b14060fe3b49a6913b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64002.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64002
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
