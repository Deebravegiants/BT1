# [M] MOOS core-moos through 10.4.0 MOOSDB Message Source Spoofing via Wire Identity

## Summary
Severity: Medium
Advisory: CVE-2026-85432
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85432
Type: osv

## Details
MOOS core-moos through 10.4.0 fails to validate client identity in MOOSDB message processing, allowing authenticated attackers to attribute writes to other clients by supplying arbitrary source identifiers in serialized messages. Attackers can forge message origins and cancel third-party subscriptions by exploiting the disconnect between authenticated connection identity and wire-supplied source attribution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85432.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85432
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-moosdb-message-source-spoofing-via-wire-identity
- https://github.com/themoos/core-moos/commit/26308f0e393f0e80bfa09b275891e776b8dbf522
- https://github.com/themoos/core-moos/pull/76
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/DB/MOOSDB.cpp#L748
