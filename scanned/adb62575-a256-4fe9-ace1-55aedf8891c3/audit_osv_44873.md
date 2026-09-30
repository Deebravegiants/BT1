# [H] Parse Server 9.0.0 Authentication Bypass via LDAP Empty Password

## Summary
Severity: High
Advisory: CVE-2026-87806
Aliases: GHSA-863r-39r9-vfcf
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87806
Type: osv

## Details
Parse Server versions <= 8.6.87 and >= 9.0.0 < 9.10.1-alpha.7 contain an authentication bypass in the built-in LDAP authentication adapter. The adapter forwarded the client-supplied password to the directory without verifying that a password had been supplied, and treated any non-error response from the directory as proof of authentication. A zero-length credential turns an LDAP simple bind into the unauthenticated authentication mechanism described in RFC 4513 section 5.1.2, which some directories (including Active Directory in its default configuration) answer with success while mapping the connection to anonymous. As a result, an unauthenticated attacker who knows a directory username can obtain a valid session token for that account, resulting in account takeover. Only deployments that enable the LDAP authentication adapter are affected, and deployments whose directory refuses unauthenticated simple bind (such as a stock OpenLDAP configuration) are not exploitable. The issue is fixed in 8.6.88 and 9.10.1-alpha.7, which require the password to be a non-empty string and reject the request before contacting the directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87806.json
- https://github.com/parse-community/parse-server/security/advisories/GHSA-863r-39r9-vfcf
- https://nvd.nist.gov/vuln/detail/CVE-2026-87806
- https://www.vulncheck.com/advisories/parse-server-9.0.0-authentication-bypass-via-ldap-empty-password
