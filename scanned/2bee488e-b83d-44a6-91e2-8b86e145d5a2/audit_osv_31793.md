# [H] net: ethernet: ti: am65-cpsw: fix memleak in certain XDP cases

## Summary
Severity: High
Advisory: CVE-2025-21788
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21788
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: ti: am65-cpsw: fix memleak in certain XDP cases

If the XDP program doesn't result in XDP_PASS then we leak the
memory allocated by am65_cpsw_build_skb().

It is pointless to allocate SKB memory before running the XDP
program as we would be wasting CPU cycles for cases other than XDP_PASS.
Move the SKB allocation after evaluating the XDP program result.

This fixes the memleak. A performance boost is seen for XDP_DROP test.

XDP_DROP test:
Before: 460256 rx/s                  0 err/s
After:  784130 rx/s                  0 err/s

## References
- https://git.kernel.org/stable/c/1bba1d042107167164a0ae3a843fdf650ab005d7
- https://git.kernel.org/stable/c/5db843258de1e4e6b1ef1cbd1797923c9e3de548
- https://git.kernel.org/stable/c/dc11f049612b9d926aca2e55f8dc9d82850d0da3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21788.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21788
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
