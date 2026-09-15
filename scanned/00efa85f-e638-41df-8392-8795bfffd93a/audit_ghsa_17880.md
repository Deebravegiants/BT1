# [M] Bouncy Castle for Java on All (API modules) allows Excessive Allocation

## Summary
Severity: Medium
Advisory: GHSA-67mf-3cr5-8w23
CVE: CVE-2025-8885
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/S:P/R:U/RE:M/U:Amber (CVSS_V4)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-67mf-3cr5-8w23
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=1.0 <1.78
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=1.0 <1.78
- Maven: `org.bouncycastle:bcprov-jdk18on` — affected >=1.0 <1.78
- Maven: `org.bouncycastle:bctls-jdk14` — affected >=1.0 <1.78
- Maven: `org.bouncycastle:bctls-jdk15to18` — affected >=1.0 <1.78
- Maven: `org.bouncycastle:bctls-jdk18on` — affected >=1.0 <1.78
- Maven: `org.bouncycastle:bc-fips` — affected >=1.0.0 <1.0.2.6
- Maven: `org.bouncycastle:bc-fips` — affected >=2.0.0 <2.0.1

## Details
A resource allocation vulnerability exists in Bouncy Castle for Java (by Legion of the Bouncy Castle Inc.) that affects all API modules. The vulnerability allows attackers to cause excessive memory allocation through unbounded resource consumption, potentially leading to denial of service. The issue is located in the ASN1ObjectIdentifier.java file in the core module.

This issue affects Bouncy Castle for Java: from BC 1.0 through 1.77, from BC-FJA 1.0.0 through 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8885
- https://github.com/bcgit/bc-java/commit/3790993df5d28f661a64439a8664343437ed3865
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-java/blob/main/core/src/main/java/org/bouncycastle/asn1/ASN1ObjectIdentifier.java
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902025%E2%80%908885
