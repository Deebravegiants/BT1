# [C] MOOS core-moos through 10.4.0 MOOSDB HTTP Server Unauthenticated Variable Write

## Summary
Severity: Critical
Advisory: CVE-2026-85428
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85428
Type: osv

## Details
MOOS core-moos through 10.4.0 contains an authentication bypass vulnerability in the optional MOOSDB HTTP server that allows unauthenticated clients to write variables. Attackers can send HTTP requests with variable names and values to the MOOSDB HTTP server port to modify MOOS variables including actuator and override commands without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85428.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85428
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-moosdb-http-server-unauthenticated-variable-write
- https://github.com/themoos/core-moos/commit/7e3aecdbf5fe47980ea9399340c77940991a6fa5
- https://github.com/themoos/core-moos/pull/77
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/DB/HTTPConnection.cpp#L196
