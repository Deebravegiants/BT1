# [H] Denial of Service in Connect2id Nimbus JOSE+JWT

## Summary
Severity: High
Advisory: GHSA-gvpg-vgmx-xg6w
CVE: CVE-2023-52428
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-11
Source: https://github.com/advisories/GHSA-gvpg-vgmx-xg6w
Type: github-advisory

## Affected
- Maven: `com.nimbusds:nimbus-jose-jwt` — affected >=0 <9.37.2

## Details
In Connect2id Nimbus JOSE+JWT before 9.37.2, an attacker can cause a denial of service (resource consumption) via a large JWE p2c header value (aka iteration count) for the PasswordBasedDecrypter (PBKDF2) component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52428
- https://bitbucket.org/connect2id/nimbus-jose-jwt
- https://bitbucket.org/connect2id/nimbus-jose-jwt/commits/3b3b77e
- https://bitbucket.org/connect2id/nimbus-jose-jwt/issues/526
- https://connect2id.com/products/nimbus-jose-jwt
