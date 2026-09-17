# [M] Nokogiri vulnerable to libxml XML Entity Expansion

## Summary
Severity: Medium
Advisory: GHSA-q7wx-62r7-j2x7
CVE: CVE-2015-1819
CWE: CWE-776
Ecosystem: RubyGems
Published: 2018-08-08
Source: https://github.com/advisories/GHSA-q7wx-62r7-j2x7
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=1.6.6.0 <1.6.6.4

## Details
The xmlreader in libxml allows remote attackers to cause a denial of service (memory consumption) via crafted XML data, related to an XML Entity Expansion (XEE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1819
- https://github.com/sparklemotion/nokogiri/issues/1374
- https://git.gnome.org/browse/libxml2/commit/?id=213f1fe0d76d30eaed6e5853057defc43e6df2c9
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2015-1819.yml
- https://security.gentoo.org/glsa/201507-08
- https://security.gentoo.org/glsa/201701-37
- https://support.apple.com/HT206166
- https://support.apple.com/HT206167
- https://support.apple.com/HT206168
- https://support.apple.com/HT206169
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00000.html
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00001.html
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00002.html
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00004.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/172710.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/172943.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00120.html
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00031.html
- http://rhn.redhat.com/errata/RHSA-2015-1419.html
- http://rhn.redhat.com/errata/RHSA-2015-2550.html
