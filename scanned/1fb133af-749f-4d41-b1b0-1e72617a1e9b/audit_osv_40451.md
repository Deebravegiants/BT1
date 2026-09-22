# [H] net: phy: clean the sfp upstream if phy probing fails

## Summary
Severity: High
Advisory: CVE-2026-53232
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53232
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: phy: clean the sfp upstream if phy probing fails

Sashiko reported that we don't call sfp_bus_del_upstream() in the probe
failure path, so let's add it, otherwise the sfp-bus is left with a
dangling 'upstream' field, that may be used later on during SFP events.

This issue existed before the generic phylib sfp support, back when
drivers were calling phy_sfp_probe themselves.

## References
- https://git.kernel.org/stable/c/0b27701ce93161d7bbf4b25fa20ca59963b0e20c
- https://git.kernel.org/stable/c/12fb84dc4dc8eb47ebe2b27f7de6255a4a205e1b
- https://git.kernel.org/stable/c/3a254779c169954fe23328a1db51f67be374f913
- https://git.kernel.org/stable/c/48774e87bbaa0056819d4b52301e4692e50e3252
- https://git.kernel.org/stable/c/9326b654f90a09eadeb796c82801a5609d57f0c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53232.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
