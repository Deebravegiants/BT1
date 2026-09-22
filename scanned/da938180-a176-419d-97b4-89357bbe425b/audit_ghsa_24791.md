# [H] Legion of the Bouncy Castle Java Cryptography API Bleichenbacher Oracle Vulnerability

## Summary
Severity: High
Advisory: GHSA-m26p-m559-g5j5
CVE: CVE-2007-6721
CWE: CWE-203
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-m26p-m559-g5j5
Type: github-advisory

## Affected
- Maven: `bouncycastle:bcprov-jdk14` — affected >=0 <1.38
- Maven: `bouncycastle:bcprov-jdk15` — affected >=0 <1.38
- Maven: `bouncycastle:bcprov-jdk16` — affected >=0 <1.38

## Details
The Legion of the Bouncy Castle Java Cryptography API before release 1.38, as used in Crypto Provider Package before 1.36, has unknown impact and remote attack vectors related to "a Bleichenbacher vulnerability in simple RSA CMS signatures without signed attributes."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6721
- https://github.com/bcgit/bc-java
- https://web.archive.org/web/20071022023551/http://www.bouncycastle.org/csharp
- https://web.archive.org/web/20080316202318/http://www.bouncycastle.org:80/releasenotes.html
- http://www.bouncycastle.org/devmailarchive/msg08195.html
