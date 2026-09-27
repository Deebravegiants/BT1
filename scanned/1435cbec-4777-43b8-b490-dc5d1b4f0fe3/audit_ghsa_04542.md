# [H] Statamic CMS's unsafe method invocation via collection sorting allows data destruction

## Summary
Severity: High
Advisory: GHSA-m92m-r54r-x8r2
CVE: CVE-2026-49287
CWE: CWE-470
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-m92m-r54r-x8r2
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.23
- Packagist: `statamic/cms` — affected >=6.0.0 <6.20.0

## Details
### Impact

The fix for GHSA-4jjr-vmv7-wh4w was incomplete. It addressed the issue in the query builder, but the same protection was not applied to in-memory collection sorting. Manipulating sort parameters could result in the loss of content and assets.

This requires a front-end template that passes request input into a tag's sort parameter. It is not exploitable by default — a template would need to be explicitly set up to sort by a visitor-controlled value.

### Patches

This has been fixed in 5.73.23 and 6.20.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-4jjr-vmv7-wh4w
- https://github.com/statamic/cms/security/advisories/GHSA-m92m-r54r-x8r2
- https://nvd.nist.gov/vuln/detail/CVE-2026-49287
- https://github.com/statamic/cms
