# [H] Use of Cryptographically Weak Pseudo-Random Number Generator (PRNG) in Pivotal CredHub Service Broker

## Summary
Severity: High
Advisory: GHSA-q3jg-4c82-j4xh
CVE: CVE-2018-15795
CWE: CWE-338
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-11-29
Source: https://github.com/advisories/GHSA-q3jg-4c82-j4xh
Type: github-advisory

## Affected
- Maven: `org.springframework.credhub:spring-credhub-core` — affected >=0 <1.1.0

## Details
Pivotal CredHub Service Broker, versions prior to 1.1.0, uses a guessable form of random number generation in creating service broker's UAA client. A remote malicious user may guess the client secret and obtain or modify credentials for users of the CredHub Service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15795
- https://github.com/advisories/GHSA-q3jg-4c82-j4xh
- https://pivotal.io/security/cve-2018-15795
- http://www.securityfocus.com/bid/105915
