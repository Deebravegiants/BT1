# [H] gollum and gollum-lib allow remote authenticated users to execute arbitrary code

## Summary
Severity: High
Advisory: GHSA-q97v-764g-r2rp
CVE: CVE-2014-9489
CWE: CWE-284
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-11-16
Source: https://github.com/advisories/GHSA-q97v-764g-r2rp
Type: github-advisory

## Affected
- RubyGems: `gollum` — affected >=0 <3.1.1
- RubyGems: `gollum-lib` — affected >=0 <4.0.1

## Details
The gollum-grit_adapter Ruby gem dependency in gollum before 3.1.1 and the gollum-lib gem dependency in gollum-lib before 4.0.1 when the string `master` is in any of the wiki documents, allows remote authenticated users to execute arbitrary code via the `-O` or `--open-files-in-pager` flags.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9489
- https://github.com/gollum/gollum/issues/913
- https://github.com/gollum/grit_adapter/commit/4520d973c81fecfebbeacd2ef2f1849d763951c7
- https://github.com/gollum/gollum
- https://web.archive.org/web/20200229041306/http://www.securityfocus.com/bid/71499
- http://www.openwall.com/lists/oss-security/2015/01/03/19
