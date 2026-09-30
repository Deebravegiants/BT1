# [M] CVE-2024-27913

## Summary
Severity: Medium
Advisory: CVE-2024-27913
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2024-27913
Type: osv

## Details
ospf_te_parse_te in ospfd/ospf_te.c in FRRouting (FRR) through 9.1 allows remote attackers to cause a denial of service (ospfd daemon crash) via a malformed OSPF LSA packet, because of an attempted access to a missing attribute field.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27913.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27913
- https://github.com/FRRouting/frr/pull/15431
