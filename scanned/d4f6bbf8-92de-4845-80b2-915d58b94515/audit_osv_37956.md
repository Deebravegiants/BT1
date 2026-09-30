# [M] LibJWT has NULL/bounds validation in JWK octet and RSA PSS parsing

## Summary
Severity: Medium
Advisory: CVE-2026-33996
Aliases: GHSA-ph96-hqpc-9f66
CVSS: 6.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:N/UI:A/VC:L/VI:L/VA:H/SC:L/SI:L/SA:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33996
Type: osv

## Details
LibJWT is a C JSON Web Token Library. Starting in version 3.0.0 and prior to version 3.3.0, the JWK parsing for RSA-PSS did not protect against a NULL value when expecting to parse JSON string values. A specially crafted JWK file could exploit this behavior by using integers in places where the code expected a string. This was fixed in v3.3.0. A workaround is available. Users importing keys through a JWK file should not do so from untrusted sources. Use the `jwk2key` tool to check for validity of a JWK file. Likewise, if possible, do not use JWK files with RSA-PSS keys.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33996.json
- https://github.com/benmcollins/libjwt/security/advisories/GHSA-ph96-hqpc-9f66
- https://nvd.nist.gov/vuln/detail/CVE-2026-33996
- https://github.com/benmcollins/libjwt/commit/cfd890286fa49ae61b534c937c9f0428b5c6034c
