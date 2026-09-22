# [H] i40e: add max boundary check for VF filters

## Summary
Severity: High
Advisory: CVE-2025-39968
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39968
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: add max boundary check for VF filters

There is no check for max filters that VF can request. Add it.

## References
- https://git.kernel.org/stable/c/02aae5fcdd34c3a55a243d80a1b328a35852a35c
- https://git.kernel.org/stable/c/77a35be582dff4c80442ebcdce24d45eed8a6ce4
- https://git.kernel.org/stable/c/8b13df5aa877b9e4541e301a58a84c42d84d2d9a
- https://git.kernel.org/stable/c/9176e18681cb0d34c5acc87bda224f5652af2ab8
- https://git.kernel.org/stable/c/cb79fa7118c150c3c76a327894bb2eb878c02619
- https://git.kernel.org/stable/c/d33e5d6631ac4fddda235a7815babc9d3f124299
- https://git.kernel.org/stable/c/e490d8c5a54e0dd1ab22417d72c3a7319cf0f030
- https://git.kernel.org/stable/c/edecce7abd7152b48e279b4fa0a883d1839bb577
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39968.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39968
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
