# [H] iommufd: Fix missing update of domains_itree after splitting iopt_area

## Summary
Severity: High
Advisory: CVE-2023-52801
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52801
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Fix missing update of domains_itree after splitting iopt_area

In iopt_area_split(), if the original iopt_area has filled a domain and is
linked to domains_itree, pages_nodes have to be properly
reinserted. Otherwise the domains_itree becomes corrupted and we will UAF.

## References
- https://git.kernel.org/stable/c/836db2e7e4565d8218923b3552304a1637e2f28d
- https://git.kernel.org/stable/c/e7250ab7ca4998fe026f2149805b03e09dc32498
- https://git.kernel.org/stable/c/fcb32111f01ddf3cbd04644cde1773428e31de6a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52801.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52801
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
