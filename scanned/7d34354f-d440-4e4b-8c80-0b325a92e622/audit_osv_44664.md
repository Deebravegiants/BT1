# [M] MOOS essential-moos through 10.0.1 pMOOSBridge Heap Corruption via Negative UDP Length

## Summary
Severity: Medium
Advisory: CVE-2026-85436
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85436
Type: osv

## Details
MOOS essential-moos through 10.0.1 contains a buffer overflow vulnerability in CMOOSUDPLink::ReadPktFromArray() that allows remote attackers to corrupt heap memory by sending UDP datagrams with negative declared lengths. Attackers can send crafted UDP packets to the configured UDPListen port to trigger an oversized memcpy operation that writes past the destination buffer, causing heap corruption and denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85436.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85436
- https://www.vulncheck.com/advisories/moos-essential-moos-through-10.0.1-pmoosbridge-heap-corruption-via-negative-udp-length
- https://github.com/themoos/essential-moos/commit/613175fcf63fb9c6c5329c4ec57c2d18588b33e2
- https://github.com/themoos/essential-moos/pull/21
- https://github.com/themoos/essential-moos
- https://github.com/themoos/essential-moos/blob/b897ea86dba8b61412dc48ac0cfb5ff34cdaf5f6/Essentials/pMOOSBridge/MOOSUDPLink.cpp#L171
