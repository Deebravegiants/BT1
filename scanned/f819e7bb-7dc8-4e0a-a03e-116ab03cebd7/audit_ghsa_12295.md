# [H] actionpack is vulnerable to denial of service via a crafted HTTP Accept header

## Summary
Severity: High
Advisory: GHSA-ffpv-c4hm-3x6v
CVE: CVE-2016-0751
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-ffpv-c4hm-3x6v
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=4.2.0 <4.2.5.1
- RubyGems: `actionpack` — affected >=0 <3.2.22.1
- RubyGems: `actionpack` — affected >=4.0.0 <4.1.14.1

## Details
actionpack/lib/action_dispatch/http/mime_type.rb in Action Pack in Ruby on Rails before 3.2.22.1, 4.0.x and 4.1.x before 4.1.14.1, 4.2.x before 4.2.5.1, and 5.x before 5.0.0.beta1.1 does not properly restrict use of the MIME type cache, which allows remote attackers to cause a denial of service (memory consumption) via a crafted HTTP Accept header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0751
- https://github.com/rails/rails/commit/127967b735813cd4f263df7a50426d74e7e9cc17
- https://github.com/rails/rails/commit/221937c8ba1d291430ceddebbd4bdef7d3cb47d6
- https://github.com/rails/rails/commit/37047b779a177b911c7161052cfc34a30e1db0af
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2016-0751.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/9oLY_FCzvoc
- https://groups.google.com/forum/message/raw?msg=ruby-security-ann/9oLY_FCzvoc/5CDXbvpYEgAJ
- https://web.archive.org/web/20160128201702/http://www.securitytracker.com/id/1034816
- https://web.archive.org/web/20200227181647/http://www.securityfocus.com/bid/81800
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178043.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178067.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00053.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00034.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00043.html
- http://rhn.redhat.com/errata/RHSA-2016-0296.html
- http://www.debian.org/security/2016/dsa-3464
- http://www.openwall.com/lists/oss-security/2016/01/25/9
