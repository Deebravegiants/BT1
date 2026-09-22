# [M] CVE-2023-23000

## Summary
Severity: Medium
Advisory: CVE-2023-23000
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-01
Source: https://osv.dev/vulnerability/CVE-2023-23000
Type: osv

## Details
In the Linux kernel before 5.17, drivers/phy/tegra/xusb.c mishandles the tegra_xusb_find_port_node return value. Callers expect NULL in the error case, but an error pointer is used.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23000.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23000
- https://security.netapp.com/advisory/ntap-20230331-0004/
- https://github.com/torvalds/linux/commit/045a31b95509c8f25f5f04ec5e0dec5cd09f2c5f
