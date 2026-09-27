# [M] OpenEMR's location resource for Group.$export operation returns entire patient/user population contact information

## Summary
Severity: Medium
Advisory: CVE-2026-25135
Aliases: GHSA-fgxg-wg4w-rj23
CVSS: 4.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25135
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions prior to 8.0.0 have an information disclosure vulnerability that leaks the entire contact information for all users, organizations, and patients in the system to anyone who has the system/(Group,Patient,*).$export operation and system/Location.read capabilities.  This vulnerability will impact OpenEMR versions since 2023. This disclosure will only occur in extremely high trust environments as it requires using a confidential client with secure key exchange that requires an administrator to enable and grant permission before the app can even be used. This will typically only occur in server-server communication across trusted clients that already have established legal agreements. Version 8.0.0 contains a patch. As a workaround, disable clients that have the vulnerable scopes and only allow clients that do not have the system/Location.read scope until a fix has been deployed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25135.json
- https://github.com/openemr/openemr/security/advisories/GHSA-fgxg-wg4w-rj23
- https://nvd.nist.gov/vuln/detail/CVE-2026-25135
- https://github.com/openemr/openemr/commit/7ab23dfe73ebd16dd66a526272f3761f1bd5be7d
