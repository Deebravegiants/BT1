# [H] Cisco node-jose improper validation of JWT signature

## Summary
Severity: High
Advisory: GHSA-jfxm-w8g2-4rcv
CVE: CVE-2018-0114
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jfxm-w8g2-4rcv
Type: github-advisory

## Affected
- npm: `node-jose` — affected >=0 <0.11.0

## Details
A vulnerability in the Cisco node-jose open source library before 0.11.0 could allow an unauthenticated, remote attacker to re-sign tokens using a key that is embedded within the token. The vulnerability is due to node-jose following the JSON Web Signature (JWS) standard for JSON Web Tokens (JWTs). This standard specifies that a JSON Web Key (JWK) representing a public key can be embedded within the header of a JWS. This public key is then trusted for verification. An attacker could exploit this by forging valid JWS objects by removing the original signature, adding a new public key to the header, and then signing the object using the (attacker-owned) private key associated with the public key embedded in that JWS header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0114
- https://github.com/cisco/node-jose
- https://github.com/cisco/node-jose/blob/master/CHANGELOG.md
- https://github.com/zi0Black/POC-CVE-2018-0114
- https://tools.cisco.com/security/center/viewAlert.x?alertId=56326
- https://web.archive.org/web/20210124130907/http://www.securityfocus.com/bid/102445
- https://www.exploit-db.com/exploits/44324
