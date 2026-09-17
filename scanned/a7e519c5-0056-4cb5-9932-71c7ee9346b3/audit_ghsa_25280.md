# [C] Bundler allows attacker to inject arbitrary code via secondary Gem source

## Summary
Severity: Critical
Advisory: GHSA-jvgm-pfqv-887x
CVE: CVE-2016-7954
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jvgm-pfqv-887x
Type: github-advisory

## Affected
- RubyGems: `bundler` — affected >=1.0.0 <2.0.0

## Details
Bundler 1.x might allow remote attackers to inject arbitrary Ruby code into an application by leveraging a gem name collision on a secondary source.  NOTE: this might overlap CVE-2013-0334.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7954
- https://github.com/bundler/bundler/issues/5051
- https://github.com/bundler/bundler/issues/5062
- https://bugzilla.redhat.com/show_bug.cgi?id=1381951
- https://collectiveidea.com/blog/archives/2016/10/06/bundlers-multiple-source-security-vulnerability
- https://github.com/rubygems/bundler
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bundler/CVE-2016-7954.yml
- https://web.archive.org/web/20170214030311/http://www.securityfocus.com/bid/93423
- http://collectiveidea.com/blog/archives/2016/10/06/bundlers-multiple-source-security-vulnerability
- http://www.openwall.com/lists/oss-security/2016/10/04/5
- http://www.openwall.com/lists/oss-security/2016/10/04/7
- http://www.openwall.com/lists/oss-security/2016/10/05/3
