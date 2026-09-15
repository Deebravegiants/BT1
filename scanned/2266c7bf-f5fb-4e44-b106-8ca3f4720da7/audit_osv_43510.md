# [H] ASoC: tegra: tegra210_ahub: Validate written enum value

## Summary
Severity: High
Advisory: CVE-2026-74292
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74292
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: tegra: tegra210_ahub: Validate written enum value

tegra_ahub_put_value_enum() reads e->values[item[0]] before
checking whether item[0] is within the enum item range. The existing
check therefore happens too late to prevent an out-of-range read of the
values array.

Move the check before the array access.

## References
- https://git.kernel.org/stable/c/1d8aabb413b5638670dfd1162169edc0ba276a2e
- https://git.kernel.org/stable/c/226d93b65f4f99b35fb7a03bdb24acb577364ebc
- https://git.kernel.org/stable/c/2ec7d16fe21c68b0879873a2abf9aac854c96134
- https://git.kernel.org/stable/c/4bcb23635d5059ee71f3fb89719ea14aada6fd59
- https://git.kernel.org/stable/c/4e45e4c2015519a39c40eb575c03b77807fb5080
- https://git.kernel.org/stable/c/964f8f9015fb117402d8d2186593397cd93388e9
- https://git.kernel.org/stable/c/e098c9c6477dfa3cb363282100108484ceba5cc5
- https://git.kernel.org/stable/c/f67d63628fe158b3a6e6b33a2b8c83ff118699d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74292.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74292
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
