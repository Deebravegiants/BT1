# [H] net: mscc: ocelot: fix use-after-free in ocelot_vlan_del()

## Summary
Severity: High
Advisory: CVE-2022-48779
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48779
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.16.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mscc: ocelot: fix use-after-free in ocelot_vlan_del()

ocelot_vlan_member_del() will free the struct ocelot_bridge_vlan, so if
this is the same as the port's pvid_vlan which we access afterwards,
what we're accessing is freed memory.

Fix the bug by determining whether to clear ocelot_port->pvid_vlan prior
to calling ocelot_vlan_member_del().

## References
- https://git.kernel.org/stable/c/c98bed60cdd7f22237ae256cc9c1c3087206b8a2
- https://git.kernel.org/stable/c/ef57640575406f57f5b3393cf57f457b0ace837e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48779.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48779
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
