# [M] CVE-2023-1855

## Summary
Severity: Medium
Advisory: CVE-2023-1855
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-1855
Type: osv

## Details
A use-after-free flaw was found in xgene_hwmon_remove in drivers/hwmon/xgene-hwmon.c in the Hardware Monitoring Linux Kernel Driver (xgene-hwmon). This flaw could allow a local attacker to crash the system due to a race problem. This vulnerability could even lead to a kernel information leak problem.

## References
- https://lore.kernel.org/all/20230318122758.2140868-1-linux%40roeck-us.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1855.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1855
- https://github.com/torvalds/linux/commit/cb090e64cf25602b9adaf32d5dfc9c8bec493cd1
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
