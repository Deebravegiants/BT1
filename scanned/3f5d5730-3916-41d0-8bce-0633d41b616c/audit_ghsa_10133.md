# [H] PAC4J has a Cross-Site Request Forgery (CSRF) Vulnerability

## Summary
Severity: High
Advisory: GHSA-xw5c-jc7x-gf75
CVE: CVE-2026-40458
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-xw5c-jc7x-gf75
Type: github-advisory

## Affected
- Maven: `org.pac4j:pac4j-core` — affected >=0 <5.7.10
- Maven: `org.pac4j:pac4j-core` — affected >=6.0.0-RC1 <6.4.1

## Details
PAC4J is vulnerable to Cross-Site Request Forgery (CSRF). A malicious attacker can craft a specially designed website which, when visited by a user, will automatically submit a forged cross-site request with a token whose hash collides with the victim's legitimate CSRF token. Importantly, the attacker does not need to know the victim’s CSRF token or its hash prior to the attack. Collisions in the deterministic String.hashCode() function can be computed directly, reducing the effective token's security space to 32 bits. This bypasses CSRF protection, allowing profile updates, password changes, account linking, and any other state-changing operations to be performed without the victim's consent.

This issue was fixed in PAC4J versions 5.7.10 and 6.4.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40458
- https://cert.pl/en/posts/2026/04/CVE-2026-40458
- https://github.com/pac4j/pac4j
- https://www.pac4j.org/blog/security-advisory-pac4j-core-and-ldap.html
