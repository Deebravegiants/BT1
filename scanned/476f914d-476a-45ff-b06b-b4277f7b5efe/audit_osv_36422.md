# [H] bonding: prevent potential infinite loop in bond_header_parse()

## Summary
Severity: High
Advisory: CVE-2026-23451
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23451
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.19 <6.18.20, >=6.19.9 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bonding: prevent potential infinite loop in bond_header_parse()

bond_header_parse() can loop if a stack of two bonding devices is setup,
because skb->dev always points to the hierarchy top.

Add new "const struct net_device *dev" parameter to
(struct header_ops)->parse() method to make sure the recursion
is bounded, and that the final leaf parse method is called.

## References
- https://git.kernel.org/stable/c/4172a7901cf43fe1cc63ef7a2ef33735ff7b7d13
- https://git.kernel.org/stable/c/946bb6cacf0ccada7bc80f1cfa07c1ed79511c1c
- https://git.kernel.org/stable/c/9532d0d0ad1d726c06f807e8f0f1ec93cbabb452
- https://git.kernel.org/stable/c/9b49c854f14f5e2d493e562a1e28d2e57fe37371
- https://git.kernel.org/stable/c/b7405dcf7385445e10821777143f18c3ce20fa04
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23451.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23451
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
