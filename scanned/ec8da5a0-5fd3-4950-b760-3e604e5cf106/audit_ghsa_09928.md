# [H] Bouncy Castle Has Covert Timing Channel Vulnerability

## Summary
Severity: High
Advisory: GHSA-p93r-85wp-75v3
CVE: CVE-2026-5598
CWE: CWE-385
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N/E:U/S:P/AU:Y/U:Red (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-p93r-85wp-75v3
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=1.71 <1.80.2
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=1.81 <1.81.1
- Maven: `org.bouncycastle:bcprov-jdk18on` — affected >=1.82 <1.84

## Details
Covert timing channel vulnerability in Legion of the Bouncy Castle Inc. BC-JAVA core on all (core modules). This vulnerability is associated with program files FrodoEngine.Java.

This issue only affects users of the FrodoKEM algorithm involved in the decryption of encapsulations.

This issue affects BC-JAVA: from 1.71 to 1.80.1, 1.81, 1.82 to 1.83.

Fixed versions: 1.80.2, 1.81.1, 1.84

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5598
- https://github.com/bcgit/bc-java/commit/8692e6b2b191fc4aafa32545c7a78bdb9bf110c5
- https://github.com/bcgit/bc-java/commit/94abbd56413dfdac651fd878bc60253871ef5e87
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%905598
- https://github.com/bcgit/bc-java/wiki/CVE-2026-5598
