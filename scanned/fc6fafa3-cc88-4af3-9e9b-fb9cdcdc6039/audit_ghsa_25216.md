# [H] LightSAML Incorrect Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-vg4f-8v9q-5c3x
CVE: CVE-2018-1000165
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vg4f-8v9q-5c3x
Type: github-advisory

## Affected
- Packagist: `lightsaml/lightsaml` — affected >=0 <1.3.5

## Details
LightSAML version prior to 1.3.5 contains a Incorrect Access Control vulnerability in signature validation in readers in `src/LightSaml/Model/XmlDSig/` that can result in impersonation of any user from Identity Provider. This vulnerability appears to have been fixed in 1.3.5 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000165
- https://github.com/lightSAML/lightSAML/commit/47cef07bb09779df15620799f3763d1b8d32307a
- https://github.com/lightSAML/lightSAML
- https://github.com/lightSAML/lightSAML/releases/tag/1.3.5
