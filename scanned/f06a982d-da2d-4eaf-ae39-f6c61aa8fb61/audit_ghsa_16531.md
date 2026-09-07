# [M] Bouncy Castle Java Cryptography API vulnerable to DNS poisoning

## Summary
Severity: Medium
Advisory: GHSA-4h8f-2wvx-gg5w
CVE: CVE-2024-34447
CWE: CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-4h8f-2wvx-gg5w
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk18on` — affected >=1.61 <1.78
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=1.61 <1.78
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=1.61 <1.78
- Maven: `org.bouncycastle:bcprov-jdk12` — affected >=1.61 <1.78
- Maven: `org.bouncycastle:bctls-fips` — affected >=0 <1.0.19
- Maven: `org.bouncycastle:bcprov-lts8on` — affected >=0 <2.73.6
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=1.61 <1.78

## Details
An issue was discovered in the Bouncy Castle Crypto Package For Java before BC TLS Java 1.0.19 (ships with BC Java 1.78, BC Java (LTS) 2.73.6) and before BC FIPS TLS Java 1.0.19. When endpoint identification is enabled in the BCJSSE and an SSL socket is created without an explicit hostname (as happens with HttpsURLConnection), hostname verification could be performed against a DNS-resolved IP address in some situations, opening up a possibility of DNS poisoning.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34447
- https://github.com/bcgit/bc-java/issues/1656
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902024%E2%80%9034447
- https://www.bouncycastle.org/latest_releases.html
- http://security.netapp.com/advisory/ntap-20240614-0007
