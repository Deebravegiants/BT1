# [H] RubyGems passenger gem allows remote attackers to delete files

## Summary
Severity: High
Advisory: GHSA-8mw8-j583-vqfg
CVE: CVE-2012-6135
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-8mw8-j583-vqfg
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=0 <4.0.0.rc4

## Details
RubyGems passenger 4.0.0 betas 1 and 2 allows remote attackers to delete arbitrary files during the startup process. 

Affects both open source and Enterprise versions (4.0.0.beta1, 4.0.0.beta2).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6135
- https://github.com/phusion/passenger/commit/8c6693e0818772c345c979840d28312c2edd4ba4
- https://github.com/phusion/passenger/commit/8c6693e0818772c345c979840d28312c2edd4ba4#commitcomment-2643541
- https://exchange.xforce.ibmcloud.com/vulnerabilities/82533
- https://github.com/phusion/passenger
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2012-6135.yml
- https://security-tracker.debian.org/tracker/CVE-2012-6135
- https://web.archive.org/web/20200918164919/https://old.blog.phusion.nl/2013/03/05/phusion-passenger-4-0-beta-1-and-2-arbitrary-file-deletion-vulnerability
- http://www.openwall.com/lists/oss-security/2013/03/02/1
