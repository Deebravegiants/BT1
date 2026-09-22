# [H] net/smc: fix neighbour and rtable leak in smc_ib_find_route()

## Summary
Severity: High
Advisory: CVE-2024-36945
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36945
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix neighbour and rtable leak in smc_ib_find_route()

In smc_ib_find_route(), the neighbour found by neigh_lookup() and rtable
resolved by ip_route_output_flow() are not released or put before return.
It may cause the refcount leak, so fix it.

## References
- https://git.kernel.org/stable/c/2ddc0dd7fec86ee53b8928a5cca5fbddd4fc7c06
- https://git.kernel.org/stable/c/5df93c029a907b0ff5a4eeadd77ba06ff0a277d2
- https://git.kernel.org/stable/c/d5a466ab6e78d6f2e0f64435f1e17246c8e941ff
- https://git.kernel.org/stable/c/da91e447d06dc649fcf46e59122e7bf8f0b2e0db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36945.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36945
- https://security.netapp.com/advisory/ntap-20250404-0006/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
