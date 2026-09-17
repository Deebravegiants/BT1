# [M] GraphQL: Security breach on Viewer query

## Summary
Severity: Medium
Advisory: GHSA-236h-rqv8-8q73
CVE: CVE-2020-15126
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-07-22
Source: https://github.com/advisories/GHSA-236h-rqv8-8q73
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=3.5.0 <4.3.0

## Details
### Impact
An authenticated user using the viewer GraphQL query can bypass all read security on his User object and can also bypass all objects linked via relation or Pointer on his User object.

### Patches
This vulnerability has been patched in Parse Server 4.3.0.

### Workarounds
No

### References
See [commit 78239ac](https://github.com/parse-community/parse-server/commit/78239ac9071167fdf243c55ae4bc9a2c0b0d89aa) for details.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-236h-rqv8-8q73
- https://nvd.nist.gov/vuln/detail/CVE-2020-15126
- https://github.com/parse-community/parse-server/commit/78239ac9071167fdf243c55ae4bc9a2c0b0d89aa
- https://github.com/parse-community/parse-server/blob/master/CHANGELOG.md#430
