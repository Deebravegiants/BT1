# [H] Insecure password handling vulnerability in Strapi

## Summary
Severity: High
Advisory: GHSA-85vg-grr5-pw42
CVE: CVE-2021-46440
CWE: CWE-922
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-04
Source: https://github.com/advisories/GHSA-85vg-grr5-pw42
Type: github-advisory

## Affected
- npm: `strapi` — affected >=0 <3.6.9
- npm: `@strapi/strapi` — affected >=4.0.0 <4.1.5

## Details
Storing passwords in a recoverable format in the DOCUMENTATION plugin component of Strapi before 3.6.9 and 4.x before 4.1.5 allows an attacker to access a victim's HTTP request. From this, the attacker can get the victim's cookie, base64 decode it, and obtain a cleartext password, leading to getting API documentation for further API attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46440
- https://github.com/strapi/strapi/pull/12246
- https://github.com/strapi/strapi
- https://hub.docker.com/r/strapi/strapi
- https://strapi.io
- http://packetstormsecurity.com/files/166915/Strapi-3.6.8-Password-Disclosure-Insecure-Handling.html
