# [M] Bouncy Castle has an LDAP injection

## Summary
Severity: Medium
Advisory: GHSA-c3fc-8qff-9hwx
CVE: CVE-2026-0636
CWE: CWE-90
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P/RE:M/U:Amber (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-c3fc-8qff-9hwx
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=1.74 <1.84
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=1.74 <1.84
- Maven: `org.bouncycastle:bcprov-jdk18on` — affected >=1.74 <1.84

## Details
Improper neutralization of special elements used in an LDAP query ('LDAP injection') vulnerability in Legion of the Bouncy Castle Inc. BC-JAVA bcprov on all (prov modules). This vulnerability is associated with program files LDAPStoreHelper.

This issue affects BC-JAVA: from 1.74 before 1.84.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0636
- https://github.com/bcgit/bc-java/commit/d20cdb8430e09224114fec0179a71859929fcbde
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%900636
