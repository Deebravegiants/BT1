# [M] spi: sn-f-ospi: Fix division by zero

## Summary
Severity: Medium
Advisory: CVE-2025-21793
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21793
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: sn-f-ospi: Fix division by zero

When there is no dummy cycle in the spi-nor commands, both dummy bus cycle
bytes and width are zero. Because of the cpu's warning when divided by
zero, the warning should be avoided. Return just zero to avoid such
calculations.

## References
- https://git.kernel.org/stable/c/3588b1c0fde2f58d166e3f94a5a58d64b893526c
- https://git.kernel.org/stable/c/4df6f005bef04a3dd16c028124a1b5684db3922b
- https://git.kernel.org/stable/c/7434135553bc03809a55803ee6a8dcaae6240d55
- https://git.kernel.org/stable/c/966328191b4c389c0f2159fa242915f51cbc1679
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21793.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21793
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
