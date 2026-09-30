# [C] MOOS core-moos through 10.4.0 Missing Authentication for MOOSDB Publish, Subscribe and DB_CLEAR

## Summary
Severity: Critical
Advisory: CVE-2026-85424
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85424
Type: osv

## Details
MOOS core-moos through 10.4.0 lacks authentication in the wire protocol, allowing unauthenticated clients to connect with full publish, subscribe, and database clear privileges. Attackers can bypass the compile-time protocol string check and connect with arbitrary client names to execute privileged operations including DB_CLEAR which resets all variables and clears client mail queues.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85424.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85424
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-missing-authentication-for-moosdb-publish-subscribe-and-db-clear
- https://github.com/themoos/core-moos/commit/5ff5cdec44242156a168cc1a545a6a21357bd3ac
- https://github.com/themoos/core-moos/pull/84
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/DB/MOOSDB.cpp#L1163
