# [M] xml2js is vulnerable to prototype pollution

## Summary
Severity: Medium
Advisory: GHSA-776f-qx25-q3cc
CVE: CVE-2023-0842
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-776f-qx25-q3cc
Type: github-advisory

## Affected
- npm: `xml2js` — affected >=0 <0.5.0

## Details
xml2js versions before 0.5.0 allows an external attacker to edit or add new properties to an object. This is possible because the application does not properly validate incoming JSON keys, thus allowing the `__proto__` property to be edited.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0842
- https://github.com/Leonidas-from-XIV/node-xml2js/issues/663
- https://github.com/Leonidas-from-XIV/node-xml2js/pull/603/commits/581b19a62d88f8a3c068b5a45f4542c2d6a495a5
- https://fluidattacks.com/advisories/myers
- https://github.com/Leonidas-from-XIV/node-xml2js
- https://lists.debian.org/debian-lts-announce/2024/03/msg00013.html
