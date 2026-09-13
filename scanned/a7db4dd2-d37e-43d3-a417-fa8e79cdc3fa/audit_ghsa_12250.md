# [H] actionpack is vulnerable to denial of service because of a wildcard controller route

## Summary
Severity: High
Advisory: GHSA-9h6g-gp95-x3q5
CVE: CVE-2015-7581
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-9h6g-gp95-x3q5
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=4.0.0 <4.2.5.1

## Details
actionpack/lib/action_dispatch/routing/route_set.rb in Action Pack in Ruby on Rails 4.x before 4.2.5.1 and 5.x before 5.0.0.beta1.1 allows remote attackers to cause a denial of service (superfluous caching and memory consumption) by leveraging an application's use of a wildcard controller route.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7581
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2015-7581.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/dthJ5wL69JE
- https://groups.google.com/forum/message/raw?msg=ruby-security-ann/dthJ5wL69JE/IdvCimtZEgAJ
- https://web.archive.org/web/20200228001849/http://www.securityfocus.com/bid/81677
- https://web.archive.org/web/20200516093752/http://www.securitytracker.com/id/1034816
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178043.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178067.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00053.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00043.html
- http://rhn.redhat.com/errata/RHSA-2016-0296.html
- http://www.debian.org/security/2016/dsa-3464
- http://www.openwall.com/lists/oss-security/2016/01/25/16
