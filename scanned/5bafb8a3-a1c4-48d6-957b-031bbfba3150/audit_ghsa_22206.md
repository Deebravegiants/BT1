# [H] OpenPGP 1.2.0 and earlier decrypts arbitrary messages

## Summary
Severity: High
Advisory: GHSA-qmvq-f3fj-m3wg
CVE: CVE-2015-8013
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qmvq-f3fj-m3wg
Type: github-advisory

## Affected
- npm: `openpgp` — affected >=0 <1.3.0

## Details
s2k.js in OpenPGP.js will decrypt arbitrary messages regardless of passphrase for crafted PGP keys which allows remote attackers to bypass authentication if message decryption is used as an authentication mechanism via a crafted symmetrically encrypted PGP message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8013
- https://github.com/openpgpjs/openpgpjs/commit/668a9bbe7033f3f475576209305eb57a54306d29
- https://github.com/openpgpjs/openpgpjs
- http://www.openwall.com/lists/oss-security/2015/10/30/5
