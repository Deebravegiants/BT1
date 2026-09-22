# [M] MOOS core-moos through 10.4.0 MOOSDB Accept Loop Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-85443
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85443
Type: osv

## Details
MOOS core-moos through 10.4.0 contains a denial of service vulnerability in MOOSCommServer::ListenLoop() where the accept thread performs a blocking receive without timeout during the wire-protocol handshake. An attacker can open a TCP connection to the MOOSDB port and send no data, causing the accept thread to block indefinitely while holding the socket-list lock, preventing all subsequent client connections.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85443.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85443
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-moosdb-accept-loop-denial-of-service
- https://github.com/themoos/core-moos/commit/8d940303949a850d4625eca2a60f27adee9c3ec4
- https://github.com/themoos/core-moos/pull/83
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/Comms/MOOSCommServer.cpp#L922
