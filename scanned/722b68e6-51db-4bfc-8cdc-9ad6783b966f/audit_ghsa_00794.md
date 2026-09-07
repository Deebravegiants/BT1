# [H] Moped Rubygem Data Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-f93j-hmcr-jcwh
CVE: CVE-2015-4410
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-08-19
Source: https://github.com/advisories/GHSA-f93j-hmcr-jcwh
Type: github-advisory

## Affected
- RubyGems: `moped` — affected >=0 <1.5.3
- RubyGems: `moped` — affected >=2.0.0 <2.0.5

## Details
`The Moped::BSON::ObjecId.legal?` method in rubygem-moped before [commit dd5a7c14b5d2e466f7875d079af71ad19774609b](https://github.com/mongoid/moped/commit/dd5a7c14b5d2e466f7875d079af71ad19774609b#diff-3b93602f64c2fe46d38efd9f73ef5358R24) allows remote attackers to cause a denial of service (worker resource consumption) or perform a cross-site scripting (XSS) attack via a crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-4410
- https://github.com/mongoid/moped/commit/dd5a7c14b5d2e466f7875d079af71ad19774609b#diff-3b93602f64c2fe46d38efd9f73ef5358R24
- https://bugzilla.redhat.com/show_bug.cgi?id=1229757
- https://github.com/mongoid/moped
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/moped/CVE-2015-4410.yml
- https://homakov.blogspot.ru/2012/05/saferweb-injects-in-various-ruby.html
- https://sakurity.com/blog/2015/06/04/mongo_ruby_regexp.html
- https://seclists.org/oss-sec/2015/q2/653
- https://web.archive.org/web/20200228085849/http://www.securityfocus.com/bid/75045
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/161964.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/161987.html
- http://sakurity.com/blog/2015/06/04/mongo_ruby_regexp.html
- http://www.openwall.com/lists/oss-security/2015/06/06/3
