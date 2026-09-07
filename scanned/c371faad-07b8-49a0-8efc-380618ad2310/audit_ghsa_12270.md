# [M] i18n gem Cross-site Scripting vulnerability 

## Summary
Severity: Medium
Advisory: GHSA-r5hc-9xx5-97rw
CVE: CVE-2013-4492
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-r5hc-9xx5-97rw
Type: github-advisory

## Affected
- RubyGems: `i18n` — affected >=0 <0.6.6

## Details
Cross-site scripting (XSS) vulnerability in exceptions.rb in the i18n gem before 0.6.6 for Ruby allows remote attackers to inject arbitrary web script or HTML via a crafted I18n::MissingTranslationData.new call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4492
- https://github.com/ruby-i18n/i18n/commit/92b57b1e4f84adcdcc3a375278f299274be62445
- https://github.com/svenfuchs/i18n/commit/92b57b1e4f84adcdcc3a375278f299274be62445
- https://access.redhat.com/errata/RHBA-2015:1100
- https://access.redhat.com/errata/RHSA-2017:0320
- https://access.redhat.com/errata/RHSA-2018:0380
- https://access.redhat.com/security/cve/CVE-2013-4492
- https://bugzilla.redhat.com/show_bug.cgi?id=1039435
- https://github.com/advisories/GHSA-r5hc-9xx5-97rw
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/i18n/CVE-2013-4492.yml
- https://github.com/svenfuchs/i18n
- https://groups.google.com/forum/#!topic/ruby-security-ann/pLrh6DUw998
- https://web.archive.org/web/20201208125214/https://groups.google.com/forum/message/raw?msg=ruby-security-ann/pLrh6DUw998/bLFEyIO4k_EJ
- https://web.archive.org/web/20210731082547/http://www.securityfocus.com/bid/64076
- http://lists.opensuse.org/opensuse-updates/2013-12/msg00093.html
- http://weblog.rubyonrails.org/2013/12/3/Rails_3_2_16_and_4_0_2_have_been_released
- http://www.debian.org/security/2013/dsa-2830
