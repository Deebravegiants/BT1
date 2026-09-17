# [M] Camaleon CMS vulnerable to Uncaught Exception

## Summary
Severity: Medium
Advisory: GHSA-r2w2-h6r8-3r53
CVE: CVE-2021-25971
CWE: CWE-248
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r2w2-h6r8-3r53
Type: github-advisory

## Affected
- RubyGems: `camaleon_cms` — affected >=2.0.1 <2.6.0.1

## Details
In Camaleon CMS, versions 2.0.1 through 2.6.0 are vulnerable to an Uncaught Exception. The app's media upload feature crashes permanently when an attacker with a low privileged access uploads a specially crafted .svg file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25971
- https://github.com/owen2345/camaleon-cms/commit/ab89584ab32b98a0af3d711e3f508a1d048147d2
- https://github.com/owen2345/camaleon-cms
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/camaleon_cms/CVE-2021-25971.yml
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25971
