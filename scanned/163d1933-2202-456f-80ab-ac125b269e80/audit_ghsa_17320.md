# [H] jose4j is vulnerable to DoS via compressed JWE content

## Summary
Severity: High
Advisory: GHSA-3677-xxcr-wjqv
CVE: CVE-2024-29371
CWE: CWE-1259
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-3677-xxcr-wjqv
Type: github-advisory

## Affected
- Maven: `org.bitbucket.b_c:jose4j` — affected >=0 <0.9.6

## Details
In jose4j before 0.9.6, an attacker can cause a Denial-of-Service (DoS) condition by crafting a malicious JSON Web Encryption (JWE) token with an exceptionally high compression ratio. When this token is processed by the server, it results in significant memory allocation and processing time during decompression.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29371
- https://bitbucket.org/b_c/jose4j/commits/19a90a64c47bb07c4aa5462f1316d5c293d81fcf
- https://bitbucket.org/b_c/jose4j/issues/220/vuln-zip-bomb-attack
- https://bitbucket.org/b_c/jose4j/wiki/Home
