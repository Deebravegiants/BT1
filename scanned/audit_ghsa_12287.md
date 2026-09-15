# [C] Incorrect Handling of Non-Boolean Comparisons During Minification in uglify-js

## Summary
Severity: Critical
Advisory: GHSA-34r7-q49f-h37c
CVE: CVE-2015-8857
CWE: CWE-1254, CWE-670
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-34r7-q49f-h37c
Type: github-advisory

## Affected
- npm: `uglify-js` — affected >=0 <2.4.24
- RubyGems: `uglifier` — affected >=0 <2.7.2

## Details
Versions of `uglify-js` prior to 2.4.24 are affected by a vulnerability which may cause crafted JavaScript to have altered functionality after minification.

## Recommendation

Upgrade UglifyJS to version >= 2.4.24.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8857
- https://github.com/mishoo/UglifyJS2/issues/751
- https://github.com/lautis/uglifier/commit/4677bfe38142937ff952f95605bcec4618892c3e
- https://github.com/mishoo/UglifyJS2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/uglifier/CVE-2015-8857.yml
- https://web.archive.org/web/20200227190830/http://www.securityfocus.com/bid/96410
- https://zyan.scripts.mit.edu/blog/backdooring-js
- http://www.openwall.com/lists/oss-security/2016/04/20/11
