# [M] MOOS core-moos through 10.4.0 MOOSDB Denial of Service via Negative Serialized String Length

## Summary
Severity: Medium
Advisory: CVE-2026-85441
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85441
Type: osv

## Details
MOOS core-moos through 10.4.0 fails to validate that serialized string lengths are non-negative in CMOOSMsg::operator>>. Unauthenticated attackers can send a crafted message with a negative length value to the MOOSDB port, causing an unhandled exception that terminates the database process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85441.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85441
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-moosdb-denial-of-service-via-negative-serialized-string-length
- https://github.com/themoos/core-moos/commit/04c92981091fdaa2ff85e2ba7eff94f6288bdbaf
- https://github.com/themoos/core-moos/pull/74
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/Comms/MOOSMsg.cpp#L453
