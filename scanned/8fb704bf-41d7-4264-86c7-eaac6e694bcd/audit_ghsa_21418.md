# [H] Parse Server is vulnerable to Prototype Pollution via Cloud Code Webhooks

## Summary
Severity: High
Advisory: GHSA-93vw-8fm5-p2jf
CVE: CVE-2022-41879
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-93vw-8fm5-p2jf
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.20
- npm: `parse-server` — affected >=5.0.0 <5.3.3

## Details
### Impact

A compromised Parse Server Cloud Code Webhook target endpoint allows an attacker to use prototype pollution to bypass the Parse Server `requestKeywordDenylist` option.

### Patches

Improved keyword detection.

### Workarounds

None.

### Collaborators

Mikhail Shcherbakov, Cristian-Alexandru Staicu and Musard Balliu working with Trend Micro Zero Day Initiative

### References

- https://github.com/parse-community/parse-server/security/advisories/GHSA-93vw-8fm5-p2jf

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-93vw-8fm5-p2jf
- https://nvd.nist.gov/vuln/detail/CVE-2022-41879
- https://github.com/parse-community/parse-server/pull/8305
- https://github.com/parse-community/parse-server/pull/8306
- https://github.com/parse-community/parse-server/commit/60c5a73d257e0d536056b38bdafef8b7130524d8
- https://github.com/parse-community/parse-server/commit/6c63f04ba37174021082a5b5c4ba1556dcc954f4
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/4.10.20
- https://github.com/parse-community/parse-server/releases/tag/5.3.3
