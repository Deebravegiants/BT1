# [M] MOOS core-moos through 10.4.0 MOOSDB Out-of-Bounds Read via Short Packet

## Summary
Severity: Medium
Advisory: CVE-2026-85455
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85455
Type: osv

## Details
MOOS core-moos through 10.4.0 contains a buffer over-read vulnerability in CMOOSCommPkt where a four-byte packet triggers out-of-bounds memory access during deserialization. Attackers can open a TCP connection to the MOOSDB port and send a crafted short packet to read memory before authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85455.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85455
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-moosdb-out-of-bounds-read-via-short-packet
- https://github.com/themoos/core-moos/commit/d30c14585753f9ae39749d9628ed15c8383f0568
- https://github.com/themoos/core-moos/pull/75
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/Comms/MOOSCommPkt.cpp#L228
