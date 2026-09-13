# [C] MOOS core-moos through 10.4.0 MOOSDB Pre-Authentication Heap Overflow via Negative Packet Length

## Summary
Severity: Critical
Advisory: CVE-2026-85440
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85440
Type: osv

## Details
MOOS core-moos through 10.4.0 contains a pre-authentication heap overflow vulnerability in MOOSCommPkt packet handling that allows remote attackers to write arbitrary data by declaring a negative packet length. Attackers can exploit the signed integer check in InflateTo() and negative size conversion in recv() to overflow a four-byte heap buffer during the HandShake phase before authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85440.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85440
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-moosdb-pre-authentication-heap-overflow-via-negative-packet-length
- https://github.com/themoos/core-moos/commit/96c49c5cdda6e07ee734a5324e8d25ba5a7f2d7a
- https://github.com/themoos/core-moos/pull/82
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/Comms/MOOSCommPkt.cpp#L67
