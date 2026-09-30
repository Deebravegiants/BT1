# [M] CVE-2024-31951

## Summary
Severity: Medium
Advisory: CVE-2024-31951
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-07
Source: https://osv.dev/vulnerability/CVE-2024-31951
Type: osv

## Details
In the Opaque LSA Extended Link parser in FRRouting (FRR) through 9.1, there can be a buffer overflow and daemon crash in ospf_te_parse_ext_link for OSPF LSA packets during an attempt to read Segment Routing Adjacency SID subTLVs (lengths are not validated).

## References
- https://github.com/FRRouting/frr/pull/15674/
- https://github.com/FRRouting/frr/pull/15674/commits/344fb4be2bc27316c74b17003c05ea40be395836
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31951.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31951
