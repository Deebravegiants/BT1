# [H] Bouncy Castle Uncontrolled Resource Consumption vulnerability

## Summary
Severity: High
Advisory: GHSA-cj8j-37rh-8475
CVE: CVE-2026-3505
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-cj8j-37rh-8475
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcpg-jdk12` — affected >=0
- Maven: `org.bouncycastle:bcpg-jdk14` — affected >=0 <1.84
- Maven: `org.bouncycastle:bcpg-jdk15` — affected >=0
- Maven: `org.bouncycastle:bcpg-jdk15to18` — affected >=0 <1.84
- Maven: `org.bouncycastle:bcpg-jdk15on` — affected >=0
- Maven: `org.bouncycastle:bcpg-jdk16` — affected >=0
- Maven: `org.bouncycastle:bcpg-jdk18on` — affected >=0 <1.84

## Details
Allocation of resources without limits or throttling vulnerability in Legion of the Bouncy Castle Inc. BC-JAVA bcpg on all (pg modules). This issue affects BC-JAVA before 1.84.

Unbounded PGP AEAD chunk size leads to pre-auth resource exhaustion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3505
- https://github.com/bcgit/bc-java/commit/dc7530939ffb6cdb57636f3609d98e23b94e71c1
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%903505
