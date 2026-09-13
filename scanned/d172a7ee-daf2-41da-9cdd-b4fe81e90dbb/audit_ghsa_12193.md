# [H] JSON gem has Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-x457-cw4h-hq5f
CVE: CVE-2013-0269
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-x457-cw4h-hq5f
Type: github-advisory

## Affected
- RubyGems: `json` — affected >=0 <1.5.5
- RubyGems: `json` — affected >=1.6.0 <1.6.8
- RubyGems: `json` — affected >=1.7.0 <1.7.7

## Details
The JSON gem before 1.5.5, 1.6.x before 1.6.8, and 1.7.x before 1.7.7 for Ruby allows remote attackers to cause a denial of service (resource consumption) or bypass the mass assignment protection mechanism via a crafted JSON document that triggers the creation of arbitrary Ruby symbols or certain internal objects, as demonstrated by conducting a SQL injection attack against Ruby on Rails, aka "Unsafe Object Creation Vulnerability."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0269
- https://exchange.xforce.ibmcloud.com/vulnerabilities/82010
- https://github.com/flori/json
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/json/CVE-2013-0269.yml
- https://groups.google.com/group/rubyonrails-security/msg/d8e0db6e08c81428?dmode=source&output=gplain
- https://web.archive.org/web/20130228082541/http://www.securityfocus.com/bid/57899
- https://web.archive.org/web/20160331131233/http://spreecommerce.com/blog/multiple-security-vulnerabilities-fixed
- https://web.archive.org/web/20160808163226/https://puppet.com/security/cve/cve-2013-0269
- http://lists.apple.com/archives/security-announce/2013/Oct/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2013-04/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2013-04/msg00015.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00034.html
- http://rhn.redhat.com/errata/RHSA-2013-0686.html
- http://rhn.redhat.com/errata/RHSA-2013-0701.html
- http://rhn.redhat.com/errata/RHSA-2013-1028.html
- http://rhn.redhat.com/errata/RHSA-2013-1147.html
- http://weblog.rubyonrails.org/2013/2/11/SEC-ANN-Rails-3-2-12-3-1-11-and-2-3-17-have-been-released
- http://www.openwall.com/lists/oss-security/2013/02/11/7
- http://www.openwall.com/lists/oss-security/2013/02/11/8
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2013&m=slackware-security.426862
