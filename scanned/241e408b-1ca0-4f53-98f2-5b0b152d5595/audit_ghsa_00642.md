# [H] Sanitize vulnerable to Improper Input Validation and Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-7f42-p84j-f58p
CVE: CVE-2018-3740
CWE: CWE-20, CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-03-21
Source: https://github.com/advisories/GHSA-7f42-p84j-f58p
Type: github-advisory

## Affected
- RubyGems: `sanitize` — affected >=3.0.0 <4.6.3

## Details
When Sanitize <= 4.6.2 is used in combination with libxml2 >= 2.9.2, a specially crafted HTML fragment can cause libxml2 to generate improperly escaped output, allowing non-whitelisted attributes to be used on whitelisted elements.

This can allow HTML and JavaScript injection, which could result in XSS if Sanitize's output is served to browsers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3740
- https://github.com/rgrove/sanitize/issues/176
- https://github.com/rgrove/sanitize/commit/01629a162e448a83d901456d0ba8b65f3b03d46e
- https://github.com/rgrove/sanitize/commit/93feeb38e21864146bb29191792b971dbe1ec62e
- https://about.gitlab.com/2018/06/25/security-release-gitlab-11-dot-0-dot-1-released
- https://github.com/rgrove/sanitize
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sanitize/CVE-2018-3740.yml
- https://www.debian.org/security/2018/dsa-4358
