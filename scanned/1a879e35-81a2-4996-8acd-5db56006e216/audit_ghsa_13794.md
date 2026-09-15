# [M] Bouncy Castle Denial of Service (DoS)

## Summary
Severity: Medium
Advisory: GHSA-wjxj-5m7g-mg7q
CVE: CVE-2023-33202
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-23
Source: https://github.com/advisories/GHSA-wjxj-5m7g-mg7q
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-ext-jdk16` — affected >=0 <1.73
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.73
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=0 <1.73
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=0 <1.73
- Maven: `org.bouncycastle:bcprov-jdk16` — affected >=0 <1.73
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0
- Maven: `org.bouncycastle:bcpkix-jdk18on` — affected >=0 <1.73
- Maven: `org.bouncycastle:bcprov-ext-jdk15on` — affected >=0 <1.73
- Maven: `org.bouncycastle:bcprov-jdk18on` — affected >=0 <1.73

## Details
Bouncy Castle for Java before 1.73 contains a potential Denial of Service (DoS) issue within the Bouncy Castle org.bouncycastle.openssl.PEMParser class. This class parses OpenSSL PEM encoded streams containing X.509 certificates, PKCS8 encoded keys, and PKCS7 objects. Parsing a file that has crafted ASN.1 data through the PEMParser causes an OutOfMemoryError, which can enable a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33202
- https://github.com/bcgit/bc-java/commit/0c576892862ed41894f49a8f639112e8d66d229c
- https://bouncycastle.org
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-java/wiki/CVE-2023-33202
- https://security.netapp.com/advisory/ntap-20240125-0001
