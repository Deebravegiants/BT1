# [H] Nokogiri subject to DoS via libxml2 vulnerability

## Summary
Severity: High
Advisory: GHSA-xjqg-9jvg-fgx2
CVE: CVE-2015-5312
CWE: CWE-400
Ecosystem: RubyGems
Published: 2018-08-21
Source: https://github.com/advisories/GHSA-xjqg-9jvg-fgx2
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=1.6.0 <1.6.7.1

## Details
The xmlStringLenDecodeEntities function in parser.c in libxml2 before 2.9.3 (as used in nokogiri before 1.6.7.1) does not properly prevent entity expansion, which allows context-dependent attackers to cause a denial of service (CPU consumption) via crafted XML data, a different vulnerability than CVE-2014-3660.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5312
- https://bugzilla.redhat.com/show_bug.cgi?id=1276693
- https://git.gnome.org/browse/libxml2/commit/?id=69030714cde66d525a8884bda01b9e8f0abf8e1e
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2015-5312.yml
- https://groups.google.com/forum/#!topic/ruby-security-ann/aSbgDiwb24s
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c04944172
- https://security.gentoo.org/glsa/201701-37
- https://support.apple.com/HT206166
- https://support.apple.com/HT206167
- https://support.apple.com/HT206168
- https://support.apple.com/HT206169
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00000.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00120.html
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00031.html
- http://marc.info/?l=bugtraq&m=145382616617563&w=2
- http://rhn.redhat.com/errata/RHSA-2015-2549.html
- http://rhn.redhat.com/errata/RHSA-2015-2550.html
- http://www.debian.org/security/2015/dsa-3430
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
