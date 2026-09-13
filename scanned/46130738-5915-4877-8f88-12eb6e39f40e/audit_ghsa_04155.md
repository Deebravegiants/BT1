# [H] Apache Directory LDAP API lacks server certificate verification for LDAP hostnames

## Summary
Severity: High
Advisory: GHSA-85rw-g4f4-jprr
CVE: CVE-2026-35563
CWE: CWE-297
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-85rw-g4f4-jprr
Type: github-advisory

## Affected
- Maven: `org.apache.directory.api:api-ldap-client-api` — affected >=2.0.0 <2.1.8

## Details
It was identified that the LDAP client implementation in version 2.1.7 does not verify if the server certificate matches the intended LDAP  hostname. While the underlying code validates the certificate chain  against a trusted authority, the absence of endpoint identification  allows a valid certificate issued for an entirely unrelated host to be improperly accepted. This oversight leaves the connection highly vulnerable to server impersonation and complete connection compromise.

The root cause of this vulnerability lies in the incomplete TLS server identity verification within the LDAP client implementation.

The attacker requires MITM capability on the network to exploit this vulnerability. This attacker must be able to present a certificate trusted by the client's configured trust store.

The hostname verification has been enforced in the new version of the LDAP API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35563
- https://github.com/apache/directory-ldap-api/commit/57a7726d8b6436c74945c12f5ba4e12d232d2bac
- https://github.com/apache/directory-ldap-api
- https://lists.apache.org/thread/5rc2nzqxp1m9wknyf93r8dnp46fhc1nn
- http://www.openwall.com/lists/oss-security/2026/06/01/2
