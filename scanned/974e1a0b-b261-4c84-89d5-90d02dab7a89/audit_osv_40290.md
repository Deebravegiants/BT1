# [H] ip6_vti: set netns_immutable on the fallback device.

## Summary
Severity: High
Advisory: CVE-2026-52909
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-52909
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6_vti: set netns_immutable on the fallback device.

john1988 and Noam Rathaus reported that vti6_init_net() does not set the
netns_immutable flag on the per-netns fallback tunnel device (ip6_vti0).

Other similar tunnel drivers (like ip6_tunnel, sit, ip6_gre, and ip_tunnel)
correctly set this flag during their fallback device initialization to
prevent them from being moved to another network namespace.

## References
- https://git.kernel.org/stable/c/12acc977838c943636fb01e2f3087d2e4cc3b7cc
- https://git.kernel.org/stable/c/12c65e2c7fef507551bd7b52123598a761662c01
- https://git.kernel.org/stable/c/7f28e3948c59481f8db9c9638e204258d26b4e41
- https://git.kernel.org/stable/c/c5dbd669db5a426b3025512322e1bf2cdbe14305
- https://git.kernel.org/stable/c/d289d5307762d1838aaece22c6b6fcad9e8865f9
- https://git.kernel.org/stable/c/dcdce3bc9f08026ff3739ee7339e1bef526fc5f3
- https://git.kernel.org/stable/c/ecf8904067dcba0dad86ece80874841e60317885
- https://git.kernel.org/stable/c/f4b6b4af7ef0661ac153c6f7eb1030aa8482c1a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52909.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52909
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
