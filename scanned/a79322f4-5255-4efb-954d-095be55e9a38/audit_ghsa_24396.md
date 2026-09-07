# [M] Bundler may install gems from a different source than expected

## Summary
Severity: Medium
Advisory: GHSA-49jx-9cmc-xjxm
CVE: CVE-2013-0334
CWE: CWE-20
Ecosystem: RubyGems
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-49jx-9cmc-xjxm
Type: github-advisory

## Affected
- RubyGems: `bundler` — affected >=0 <1.7.0

## Details
Bundler before 1.7, when multiple top-level source lines are used, allows remote attackers to install arbitrary gems by creating a gem with the same name as another gem in a different source.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0334
- https://github.com/rubygems/bundler
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bundler/CVE-2013-0334.yml
- https://security.gentoo.org/glsa/201609-02
- https://web.archive.org/web/20210122060358/https://www.securityfocus.com/bid/70099
- http://bundler.io/blog/2014/08/14/bundler-may-install-gems-from-a-different-source-than-expected-cve-2013-0334.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-October/140609.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-October/140654.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-October/140655.html
- http://lists.opensuse.org/opensuse-updates/2015-03/msg00092.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
