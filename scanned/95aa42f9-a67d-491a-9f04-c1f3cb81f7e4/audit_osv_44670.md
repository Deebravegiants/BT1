# [M] MOOS core-moos through 10.4.0 MOOSDB Denial of Service via Unbounded Packet Allocation

## Summary
Severity: Medium
Advisory: CVE-2026-85442
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85442
Type: osv

## Details
MOOS core-moos through 10.4.0 fails to validate packet length declarations in CMOOSCommPkt::OnBytesWritten(), allowing unauthenticated attackers to trigger unbounded buffer allocation by sending crafted wire packets. Attackers can send packets with large declared lengths to exhaust server memory and cause denial of service before client authentication completes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85442.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85442
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-moosdb-denial-of-service-via-unbounded-packet-allocation
- https://github.com/themoos/core-moos/commit/e7ea624a7b7828b47fcd35fc43feec1f5cfbbe21
- https://github.com/themoos/core-moos/pull/81
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/Comms/MOOSCommPkt.cpp#L99
