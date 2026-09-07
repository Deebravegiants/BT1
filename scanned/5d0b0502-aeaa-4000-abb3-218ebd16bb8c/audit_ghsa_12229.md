# [M] RDoc contains XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v2r9-c84j-v7xm
CVE: CVE-2013-0256
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-v2r9-c84j-v7xm
Type: github-advisory

## Affected
- RubyGems: `rdoc` — affected >=2.3.0 <3.12.1

## Details
darkfish.js in RDoc 2.3.0 through 3.12 and 4.x before 4.0.0.preview2.1, as used in Ruby, does not properly generate documents, which allows remote attackers to conduct cross-site scripting (XSS) attacks via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0256
- https://github.com/rdoc/rdoc/commit/ffa87887ee0517793df7541629a470e331f9fe60
- https://bugzilla.redhat.com/show_bug.cgi?id=907820
- https://github.com/advisories/GHSA-v2r9-c84j-v7xm
- https://github.com/rdoc/rdoc
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rdoc/CVE-2013-0256.yml
- https://web.archive.org/web/20130402173730/http://blog.segment7.net:80/2013/02/06/rdoc-xss-vulnerability-cve-2013-0256-releases-3-9-5-3-12-1-4-0-0-rc-2
- http://lists.opensuse.org/opensuse-security-announce/2013-04/msg00015.html
- http://lists.opensuse.org/opensuse-updates/2013-02/msg00048.html
- http://rhn.redhat.com/errata/RHSA-2013-0686.html
- http://rhn.redhat.com/errata/RHSA-2013-0701.html
- http://rhn.redhat.com/errata/RHSA-2013-0728.html
- http://www.ruby-lang.org/en/news/2013/02/06/rdoc-xss-cve-2013-0256
- http://www.ubuntu.com/usn/USN-1733-1
