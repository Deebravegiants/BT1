# [M] MOOS-IvP through 24.8.1 BHV_IPF Demultiplexer Memory Exhaustion via Packet Count

## Summary
Severity: Medium
Advisory: CVE-2026-85445
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85445
Type: osv

## Details
MOOS-IvP through 24.8.1 contains a denial of service vulnerability in the Demuxer::addMuxPacket() function that trusts the packet count declared in mux headers without validation. Attackers can declare arbitrarily large packet counts to trigger unbounded memory allocation, exhausting system resources and causing service unavailability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85445.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85445
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-bhv-ipf-demultiplexer-memory-exhaustion-via-packet-count
- https://github.com/moos-ivp/moos-ivp/commit/fc5649ac12915f66a9f09520cdb6b14bc6d77595
- https://github.com/moos-ivp/moos-ivp/pull/129
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/lib_ivpbuild/Demuxer.cpp#L79
