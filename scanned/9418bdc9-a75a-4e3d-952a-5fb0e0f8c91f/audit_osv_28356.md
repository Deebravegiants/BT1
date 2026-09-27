# [M] CVE-2024-31950

## Summary
Severity: Medium
Advisory: CVE-2024-31950
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-04-07
Source: https://osv.dev/vulnerability/CVE-2024-31950
Type: osv

## Details
In FRRouting (FRR) through 9.1, there can be a buffer overflow and daemon crash in ospf_te_parse_ri for OSPF LSA packets during an attempt to read Segment Routing subTLVs (their size is not validated).

## References
- https://github.com/FRRouting/frr/pull/15674/
- https://github.com/FRRouting/frr/pull/15674/commits/6b84541df71772f697a7f9e6b2aaf72536aab775
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31950.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31950
