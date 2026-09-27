# [H] ipv6: mcast: Delay put pmc->idev in mld_del_delrec()

## Summary
Severity: High
Advisory: CVE-2025-38550
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38550
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: mcast: Delay put pmc->idev in mld_del_delrec()

pmc->idev is still used in ip6_mc_clear_src(), so as mld_clear_delrec()
does, the reference should be put after ip6_mc_clear_src() return.

## References
- https://git.kernel.org/stable/c/1b5b413094af8d88a31b5df3fd262f6baca53841
- https://git.kernel.org/stable/c/5f18e0130194550dff734e155029ae734378b5ea
- https://git.kernel.org/stable/c/6e4eec86fe5f6b3fdbc702d1d36ac2a6e7ec0806
- https://git.kernel.org/stable/c/728db00a14cacb37f36e9382ab5fad55caf890cc
- https://git.kernel.org/stable/c/7929d27c747eafe8fca3eecd74a334503ee4c839
- https://git.kernel.org/stable/c/ae3264a25a4635531264728859dbe9c659fad554
- https://git.kernel.org/stable/c/dcbc346f50a009d8b7f4e330f9f2e22d6442fa26
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38550.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38550
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
