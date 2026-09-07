# [M] administrate vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-cc8c-26rj-v2vx
CVE: CVE-2016-3098
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-cc8c-26rj-v2vx
Type: github-advisory

## Affected
- RubyGems: `administrate` — affected >=0 <0.1.5

## Details
Cross-site request forgery (CSRF) vulnerability in administrate 0.1.4 and earlier allows remote attackers to hijack the user's OAuth autorization code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3098
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/administrate/CVE-2016-3098.yml
- https://github.com/thoughtbot/administrate
- https://seclists.org/oss-sec/2016/q2/0
