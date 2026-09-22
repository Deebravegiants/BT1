# [H] Infinite Loop in scapy

## Summary
Severity: High
Advisory: GHSA-mpf2-q34c-fc6j
CVE: CVE-2019-1010142
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-07-22
Source: https://github.com/advisories/GHSA-mpf2-q34c-fc6j
Type: github-advisory

## Affected
- PyPI: `scapy` — affected >=2.4-rc1 <2.4.1

## Details
scapy is affected by a Denial of Service vulnerability resulting in an infinite loop and resource consumption rendering the program unresponsive. The component is: `_RADIUSAttrPacketListField.getfield(self..)`. The attack vector is over the network or in a pcap. both work.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010142
- https://github.com/secdev/scapy/pull/1409
- https://github.com/secdev/scapy/pull/1409/files#diff-441eff981e466959968111fc6314fe93L1058
- https://github.com/pypa/advisory-database/tree/main/vulns/scapy/PYSEC-2019-120.yaml
- https://github.com/secdev/scapy
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/42NRPMC3NS2QVFNIXYP6WV2T3LMLLY7E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T46XW4S5BCA3VV3JT3C5Q6LBEXSIACLN
- https://www.imperva.com/blog/scapy-sploit-python-network-tool-is-vulnerable-to-denial-of-service-dos-attack-cve-pending
