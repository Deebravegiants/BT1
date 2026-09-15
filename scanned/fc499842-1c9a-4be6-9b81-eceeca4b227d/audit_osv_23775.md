# [M] net: phy: micrel: Allow probing without .driver_data

## Summary
Severity: Medium
Advisory: CVE-2022-49472
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49472
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: phy: micrel: Allow probing without .driver_data

Currently, if the .probe element is present in the phy_driver structure
and the .driver_data is not, a NULL pointer dereference happens.

Allow passing .probe without .driver_data by inserting NULL checks
for priv->type.

## References
- https://git.kernel.org/stable/c/143878e18001c5a61fcc7ae5c5240323753bb641
- https://git.kernel.org/stable/c/1e5fbfc2a6f384e3195446c14bbd3bc298eb88c2
- https://git.kernel.org/stable/c/660dfa033ccc9afb032015b6dc76e846bba42cfb
- https://git.kernel.org/stable/c/7dcb404662839a4ed1a9703658fee979eb894ca4
- https://git.kernel.org/stable/c/91e720b32cba25fa58eaa4c88fe957009cffe9f3
- https://git.kernel.org/stable/c/abb5594ae2ba7b82cce85917cc6337ec5d774837
- https://git.kernel.org/stable/c/bd219273b4e004a3f853da72e111fc8f81357501
- https://git.kernel.org/stable/c/f2ef6f7539c68c6bd6c32323d8845ee102b7c450
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49472.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49472
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
