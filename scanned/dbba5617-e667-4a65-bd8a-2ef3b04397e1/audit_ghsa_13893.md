# [H] semver-tags is vulnerable to Command Injection via the getGitTagsRemote function

## Summary
Severity: High
Advisory: GHSA-8h3g-hcwp-6hxq
CVE: CVE-2022-25853
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-06
Source: https://github.com/advisories/GHSA-8h3g-hcwp-6hxq
Type: github-advisory

## Affected
- npm: `semver-tags` — affected >=0

## Details
All versions of the package semver-tags are vulnerable to Command Injection via the getGitTagsRemote function due to improper input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25853
- https://github.com/jtrussell/semver-tags
- https://github.com/jtrussell/semver-tags/blob/db1ba680bafed0d51e1bb36bd38f2c5439fe8b00/lib/get-tags.js#L21
- https://github.com/jtrussell/semver-tags/blob/db1ba680bafed0d51e1bb36bd38f2c5439fe8b00/lib/get-tags.js%23L21
- https://security.snyk.io/vuln/SNYK-JS-SEMVERTAGS-3175612
