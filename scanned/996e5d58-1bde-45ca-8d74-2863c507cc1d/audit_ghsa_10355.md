# [M] Bouncy Castle Crypto Package For Java: Use of a Broken or Risky Cryptographic Algorithm vulnerability in bcpkix modules

## Summary
Severity: Medium
Advisory: GHSA-wg6q-6289-32hp
CVE: CVE-2026-5588
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/U:Green (CVSS_V4)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-wg6q-6289-32hp
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcpkix-jdk18on` — affected >=1.49 <1.84
- Maven: `org.bouncycastle:bcpkix-jdk15to18` — affected >=1.49 <1.84
- Maven: `org.bouncycastle:bcpkix-jdk15on` — affected >=1.49 <1.84
- Maven: `org.bouncycastle:bcpkix-jdk14` — affected >=1.49 <1.84
- Maven: `org.bouncycastle:bcpkix-debug-jdk18on` — affected >=1.49 <1.84
- Maven: `org.bouncycastle:bcpkix-debug-jdk15to18` — affected >=1.49 <1.84
- Maven: `org.bouncycastle:bcpkix-debug-jdk14` — affected >=1.49 <1.84

## Details
: Use of a Broken or Risky Cryptographic Algorithm vulnerability in Legion of the Bouncy Castle Inc. BC-JAVA bcpkix on all (pkix modules).


PKIX draft CompositeVerifier accepts empty signature sequence as valid.


This issue affects BC-JAVA: from 1.49 before 1.84.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5588
- https://github.com/bcgit/bc-java/commit/656bae0dbd9b1521f840521ff786e78749fe3057
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%905588
