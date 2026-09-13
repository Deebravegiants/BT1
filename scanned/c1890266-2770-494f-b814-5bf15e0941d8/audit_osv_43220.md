# [M] Budibase before 3.40.0 Credential Exposure via STRING Fields

## Summary
Severity: Medium
Advisory: CVE-2026-72857
Aliases: GHSA-6mpp-gfg5-x2vv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72857
Type: osv

## Details
Budibase before 3.40.0 fails to redact datasource credentials stored in STRING typed fields, allowing authenticated users to read MongoDB connection strings and Firebase private keys in plaintext. Attackers with table read permissions can retrieve datasource configurations through the read API to obtain live backend database credentials and service account keys.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-6mpp-gfg5-x2vv
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72857.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72857
- https://www.vulncheck.com/advisories/budibase-before-credential-exposure-via-string-fields
