# [H] wifi: nl80211: Avoid address calculations via out of bounds array indexing

## Summary
Severity: High
Advisory: CVE-2024-38562
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38562
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: nl80211: Avoid address calculations via out of bounds array indexing

Before request->channels[] can be used, request->n_channels must be set.
Additionally, address calculations for memory after the "channels" array
need to be calculated from the allocation base ("request") rather than
via the first "out of bounds" index of "channels", otherwise run-time
bounds checking will throw a warning.

## References
- https://git.kernel.org/stable/c/4e2a5566462b53db7d4c4722da86eedf0b8f546c
- https://git.kernel.org/stable/c/838c7b8f1f278404d9d684c34a8cb26dc41aaaa1
- https://git.kernel.org/stable/c/8fa4d56564ee7cc2ee348258d88efe191d70dd7f
- https://git.kernel.org/stable/c/ed74398642fcb19f6ff385c35a7d512c6663e17b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38562.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38562
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
