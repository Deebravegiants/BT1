# [M] MOOS core-moos through 10.4.0 MOOSDB HTTP Server Resource Exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-85450
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85450
Type: osv

## Details
MOOS core-moos through 10.4.0 contains a denial of service vulnerability in the MOOSDB HTTP server that creates unbounded connections and threads without limits. Attackers can open many connections and send endless header data to exhaust server threads and memory, causing service unavailability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85450
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-moosdb-http-server-resource-exhaustion
- https://github.com/themoos/core-moos/commit/dfef92b3bc31886bc47e4d680aef583b78cb8d72
- https://github.com/themoos/core-moos/pull/79
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/DB/HTTPConnection.cpp#L167
