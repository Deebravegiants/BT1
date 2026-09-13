# [M] Improper Authorization in aedes

## Summary
Severity: Medium
Advisory: GHSA-4cmx-hrq9-c23p
CVE: CVE-2018-3778
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2018-08-15
Source: https://github.com/advisories/GHSA-4cmx-hrq9-c23p
Type: github-advisory

## Affected
- npm: `aedes` — affected >=0 <0.35.1

## Details
Versions of `aedes` before 0.35.1 does not respect its own authorization rules when a client sets a `Last Will`.


## Recommendation

Update to version 0.35.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3778
- https://github.com/moscajs/aedes/issues/211
- https://github.com/moscajs/aedes/issues/212
- https://github.com/moscajs/aedes/commit/ffbc1702bb24b596afbb96407cc6db234a4044a8
- https://github.com/moscajs/aedes
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/457.json
