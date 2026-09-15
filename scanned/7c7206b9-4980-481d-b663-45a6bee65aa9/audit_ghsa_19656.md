# [M] CGI has Regular Expression Denial of Service (ReDoS) potential in Util#escapeElement

## Summary
Severity: Medium
Advisory: GHSA-mhwm-jh88-3gjf
CVE: CVE-2025-27220
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-mhwm-jh88-3gjf
Type: github-advisory

## Affected
- RubyGems: `cgi` — affected >=0 <0.3.5.1
- RubyGems: `cgi` — affected >=0.3.6 <0.3.7
- RubyGems: `cgi` — affected >=0.4.0 <0.4.2

## Details
There is a possibility for Regular expression Denial of Service (ReDoS) by in the cgi gem. This vulnerability has been assigned the CVE identifier CVE-2025-27220. We recommend upgrading the cgi gem.

## Details

The regular expression used in `CGI::Util#escapeElement` is vulnerable to ReDoS. The crafted input could lead to a high CPU consumption.

This vulnerability only affects Ruby 3.1 and 3.2. If you are using these versions, please update CGI gem to version 0.3.5.1, 0.3.7, 0.4.2 or later.

## Affected versions

cgi gem versions <= 0.3.5, 0.3.6, 0.4.0 and 0.4.1.

## Credits

Thanks to svalkanov for discovering this issue.
Also thanks to nobu for fixing this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27220
- https://github.com/ruby/cgi/pull/52
- https://github.com/ruby/cgi/pull/53
- https://github.com/ruby/cgi/pull/54
- https://hackerone.com/reports/2890322
- https://github.com/ruby/cgi
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/cgi/CVE-2025-27220.yml
- https://lists.debian.org/debian-lts-announce/2025/03/msg00008.html
- https://www.cve.org/CVERecord?id=CVE-2025-27220
- https://www.ruby-lang.org/en/news/2025/02/26/security-advisories
