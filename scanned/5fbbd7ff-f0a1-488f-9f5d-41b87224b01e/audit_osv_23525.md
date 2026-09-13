# [M] net: ethernet: stmmac: fix altr_tse_pcs function when using a fixed-link

## Summary
Severity: Medium
Advisory: CVE-2022-49061
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49061
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.190, >=5.5.0 <5.10.112, >=5.11.0 <5.15.35, >=5.16.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: stmmac: fix altr_tse_pcs function when using a fixed-link

When using a fixed-link, the altr_tse_pcs driver crashes
due to null-pointer dereference as no phy_device is provided to
tse_pcs_fix_mac_speed function. Fix this by adding a check for
phy_dev before calling the tse_pcs_fix_mac_speed() function.

Also clean up the tse_pcs_fix_mac_speed function a bit. There is
no need to check for splitter_base and sgmii_adapter_base
because the driver will fail if these 2 variables are not
derived from the device tree.

## References
- https://git.kernel.org/stable/c/08d5e3e954537931c8da7428034808d202e98299
- https://git.kernel.org/stable/c/62a48383ebe2e159fd68425dd3e16d4c6bd6599a
- https://git.kernel.org/stable/c/6c020f05253df04c3480b586fe188a3582740049
- https://git.kernel.org/stable/c/7e59fdf9547c4f948d1d917ec7ffa5fb5ac53bdb
- https://git.kernel.org/stable/c/a6aaa00324240967272b451bfa772547bd576ee6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49061.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49061
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
