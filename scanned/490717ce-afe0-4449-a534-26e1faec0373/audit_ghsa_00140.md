# [M] Heap-based buffer overflow in nokogiri

## Summary
Severity: Medium
Advisory: GHSA-jxjr-5h69-qw3w
CVE: CVE-2015-7499
CWE: CWE-119
Ecosystem: RubyGems
Published: 2018-09-17
Source: https://github.com/advisories/GHSA-jxjr-5h69-qw3w
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=1.6.0 <1.6.7.2

## Details
Heap-based buffer overflow in the xmlGROW function in parser.c in libxml2 before 2.9.3.  A remote attacker could provide a specially crafted XML or HTML file that, when processed by an application using libxml2, would cause that application to use an excessive amount of CPU, leak potentially sensitive information, or crash the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7499
- https://bugzilla.redhat.com/show_bug.cgi?id=1281925
- https://git.gnome.org/browse/libxml2/commit/?id=28cd9cb747a94483f4aea7f0968d202c20bb4cfc
- https://git.gnome.org/browse/libxml2/commit/?id=35bcb1d758ed70aa7b257c9c3b3ff55e54e3d0da
- https://github.com/advisories/GHSA-jxjr-5h69-qw3w
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2015-7499.yml
- https://groups.google.com/forum/#!topic/ruby-security-ann/Dy7YiKb_pMM
- https://security.gentoo.org/glsa/201701-37
- https://web.archive.org/web/20210724022841/http://www.securityfocus.com/bid/79509
- https://web.archive.org/web/20211205133229/https://securitytracker.com/id/1034243
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00120.html
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00031.html
- http://rhn.redhat.com/errata/RHSA-2015-2549.html
- http://rhn.redhat.com/errata/RHSA-2015-2550.html
- http://www.debian.org/security/2015/dsa-3430
- http://www.ubuntu.com/usn/USN-2834-1
- http://xmlsoft.org/news.html
