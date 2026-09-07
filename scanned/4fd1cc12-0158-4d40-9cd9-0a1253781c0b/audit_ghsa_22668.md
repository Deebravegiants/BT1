# [H] RubyGems vulnerable to DNS hijack attack

## Summary
Severity: High
Advisory: GHSA-wp3j-rvfp-624h
CVE: CVE-2015-3900
CWE: CWE-350
Ecosystem: RubyGems
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wp3j-rvfp-624h
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=2.0.0 <2.0.16
- RubyGems: `rubygems-update` — affected >=2.2.0 <2.2.4
- RubyGems: `rubygems-update` — affected >=2.4.0 <2.4.7

## Details
RubyGems 2.0.x before 2.0.16, 2.2.x before 2.2.4, and 2.4.x before 2.4.7 does not validate the hostname when fetching gems or making API requests, which allows remote attackers to redirect requests to arbitrary domains via a crafted DNS SRV record, aka a "DNS hijack attack."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3900
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubygems-update/CVE-2015-3900.yml
- https://puppet.com/security/cve/CVE-2015-3900
- https://web.archive.org/web/20170331091241/https://puppet.com/security/cve/CVE-2015-3900
- https://web.archive.org/web/20200228055155/http://www.securityfocus.com/bid/75482
- https://www.trustwave.com/Resources/Security-Advisories/Advisories/TWSL2015-007/?fid=6356
- https://www.trustwave.com/Resources/SpiderLabs-Blog/Attacking-Ruby-Gem-Security-with-CVE-2015-3900
- http://blog.rubygems.org/2015/05/14/CVE-2015-3900.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-August/163502.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-August/163600.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-August/164236.html
- http://rhn.redhat.com/errata/RHSA-2015-1657.html
- http://www.openwall.com/lists/oss-security/2015/06/26/2
- http://www.oracle.com/technetwork/topics/security/bulletinoct2015-2511968.html
