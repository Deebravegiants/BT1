# [C] DbGate through 7.2.6 Arbitrary File Read and Write via file:// jslid

## Summary
Severity: Critical
Advisory: CVE-2026-85176
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85176
Type: osv

## Details
DbGate fails to validate jslid parameters in the jsldata controller, allowing authenticated users to read and write arbitrary files via file:// scheme resolution. Attackers can exploit getJslFileName() to bypass directory containment and access sensitive files including encrypted database credentials stored in connections configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85176.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85176
- https://www.vulncheck.com/advisories/dbgate-through-7.2.6-arbitrary-file-read-and-write-via-file-jslid
- https://github.com/dbgate/dbgate/issues/1502
- https://github.com/dbgate/dbgate
- https://github.com/dbgate/dbgate/blob/v7.2.6/packages/api/src/controllers/jsldata.js
- https://github.com/dbgate/dbgate/blob/v7.2.6/packages/api/src/utility/getJslFileName.js
