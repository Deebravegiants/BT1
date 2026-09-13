# [M] CVE-2022-40817

## Summary
Severity: Medium
Advisory: CVE-2022-40817
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-09-27
Source: https://osv.dev/vulnerability/CVE-2022-40817
Type: osv

## Details
Zammad 5.2.1 has a fine-grained permission model that allows to configure read-only access to tickets. However, agents were still wrongly able to perform some operations on such tickets, like adding and removing links, tags. and related answers. This issue has been fixed in 5.2.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40817.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40817
- https://zammad.com/de/advisories/zaa-2022-10
