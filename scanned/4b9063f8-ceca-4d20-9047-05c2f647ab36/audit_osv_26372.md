# [M] net: phy: dp83822: Fix null pointer access on DP83825/DP83826 devices

## Summary
Severity: Medium
Advisory: CVE-2023-52984
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52984
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.168, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: phy: dp83822: Fix null pointer access on DP83825/DP83826 devices

The probe() function is only used for the DP83822 PHY, leaving the
private data pointer uninitialized for the smaller DP83825/26 models.
While all uses of the private data structure are hidden in 82822 specific
callbacks, configuring the interrupt is shared across all models.
This causes a NULL pointer dereference on the smaller PHYs as it accesses
the private data unchecked. Verifying the pointer avoids that.

## References
- https://git.kernel.org/stable/c/2cd1e9c013ec56421c58921b1ddf1d2d53bd47fa
- https://git.kernel.org/stable/c/362a2f5531dc0e5b0b5b3e3a541000dbffa75461
- https://git.kernel.org/stable/c/422ae7d9c7221e8d4c8526d0f54106307d69d2dc
- https://git.kernel.org/stable/c/78901b10522cdf6badf24acf65a892637596bccc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52984.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52984
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
