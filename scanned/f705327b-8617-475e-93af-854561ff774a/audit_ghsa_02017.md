# [M] Passing in a non-string 'html' argument can lead to unsanitized output

## Summary
Severity: Medium
Advisory: GHSA-qxg5-2qff-p49r
CVE: CVE-2021-32696
CWE: CWE-241, CWE-79, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-qxg5-2qff-p49r
Type: github-advisory

## Affected
- npm: `striptags` — affected >=0 <3.2.0

## Details
A type-confusion vulnerability can cause `striptags` to concatenate unsanitized strings when an array-like object is passed in as the `html` parameter. This can be abused by an attacker who can control the shape of their input, e.g. if query parameters are passed directly into the function.

### Impact

XSS

### Patches

`3.2.0`

### Workarounds

Ensure that the `html` parameter is a string before calling the function.

## References
- https://github.com/ericnorris/striptags/security/advisories/GHSA-qxg5-2qff-p49r
- https://nvd.nist.gov/vuln/detail/CVE-2021-32696
- https://github.com/ericnorris/striptags/commit/f252a6b0819499cd65403707ebaf5cc925f2faca
- https://github.com/ericnorris/striptags/releases/tag/v3.2.0
- https://www.npmjs.com/package/striptags
